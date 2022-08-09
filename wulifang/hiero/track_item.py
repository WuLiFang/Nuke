# -*- coding=UTF-8 -*-
# pyright: strict, reportTypeCommentUsage=false

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import re

from wulifang.vendor.six import iteritems, itervalues, python_2_unicode_compatible

import hiero.core
import hiero.ui

from .. import codectools

_LOGGER = logging.getLogger(__name__)
TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import (
        Callable,
        Dict,
        Iterator,
        List,
        Optional,
        Sequence,
        Set,
        Text,
        Tuple,
        Union,
    )


def selection():
    # type: () -> Iterator[hiero.core.TrackItem]
    seq = hiero.ui.activeSequence()
    if not seq:
        return
    te = hiero.ui.getTimelineEditor(seq)
    if not te:
        return
    for i in te.selection():
        if isinstance(i, hiero.core.TrackItem):
            yield i
            continue
        if isinstance(i, (hiero.core.VideoTrack, hiero.core.AudioTrack)):
            for j in i.items():
                yield j
            continue
        _LOGGER.warning("unexpected selection item: %s", i)


def has_selection():
    try:
        _ = next(selection())
        return True
    except StopIteration:
        return False


def group_by_project(items):
    # type: (Iterator[hiero.core.TrackItem]) -> Iterator[Tuple[Optional[hiero.core.Project], Sequence[hiero.core.TrackItem]]]

    buf = []  # type: Sequence[hiero.core.TrackItem]
    p_last = None  # type: Optional[hiero.core.Project]
    for i in items:
        p_current = i.project()
        if buf and p_current != p_last:
            yield p_last, buf
            buf = []
        p_last = p_current
        buf.append(i)
    yield p_last, buf


@python_2_unicode_compatible
class _NameCounter:
    def __init__(self):
        self._m = {}  # type: Dict[Text, int]

    def get(self, name):
        # type: (Text) -> int
        return self._m.get(name, 0)

    def add(self, name, value=1):
        # type: (Text, int) -> int
        self._m.setdefault(name, 0)
        self._m[name] += value
        return self.get(name)

    def items(self):
        return (i for i in iteritems(self._m) if i[1])

    def total(self):
        return sum(count for _, count in self.items())

    def __bool__(self):
        return self.total() > 0

    __nonzero__ = __bool__

    def __str__(self):
        details = ""
        for name, count in self.items():
            details += "'%s'=%d;" % (name, count)
        if details:
            details = "(%s)" % details
        return "%d%s" % (self.total(), details)


class AlignPlan:
    def __init__(self):
        # (name, count) as key
        self._m = {}  # type: Dict[Tuple[Text, int], Tuple[int, int,float, float]]
        self._counter = _NameCounter()
        self.aligned_count = _NameCounter()
        self.ignored_count = _NameCounter()
        self.created_count = _NameCounter()
        self.moved_to_end_count = _NameCounter()

    def explain(self):
        # type: () -> Text
        def _counter_detail(counter):
            # type: (_NameCounter) -> Text
            ret = ""
            for name, count in counter.items():
                ret += "  %s\t%d\n" % (name, count)
            return ret

        ret = "已对齐 %d 项：\n" % self.aligned_count.total()
        ret += _counter_detail(self.aligned_count)

        if self.created_count:
            ret += "创建 %d 项：\n" % self.created_count.total()
            ret += _counter_detail(self.created_count)
        if self.ignored_count:
            ret += "忽略 %d 项：\n" % self.ignored_count.total()
            ret += _counter_detail(self.ignored_count)
        if self.moved_to_end_count:
            ret += "将 %d 范围冲突项移至末尾：\n" % self.moved_to_end_count.total()
            ret += _counter_detail(self.moved_to_end_count)
        return ret

    def add_base_item(self, item):
        # type: (hiero.core.TrackItem,) -> None
        name = item.name().decode("utf-8")
        key = (name, self._counter.add(name))
        t_in0, t_out0, s_in0, s_out0 = (
            item.timelineIn(),
            item.timelineOut(),
            item.sourceIn(),
            item.sourceOut(),
        )
        assert key not in self._m, "key should be unique"
        for k, v in iteritems(self._m):
            t_in, t_out, _, _ = v
            if t_in0 < t_in < t_out0 or t_in0 < t_out < t_out0:
                raise ValueError(
                    "时间范围冲突: %s(%d-%d),%s(%d-%d)"
                    % (
                        k[0],
                        t_in,
                        t_out,
                        name,
                        t_in0,
                        t_out0,
                    )
                )
        self._m[key] = (t_in0, t_out0, s_in0, s_out0)

    def apply_to_track(self, track):
        # type: (Union[hiero.core.VideoTrack, hiero.core.AudioTrack]) -> None
        track_items = list(track.items())
        if not track_items:
            return
        # assume items is sorted
        track_length = track_items[-1].timelineOut() - track_items[0].timelineIn()
        track_name = codectools.text(track.name())

        cleanups = []  # type: List[Callable[[],None]]

        def _move_to_end(i):
            # type: (hiero.core.TrackItem) -> None

            def _move_back():
                try:
                    i.move(-track_length)
                except RuntimeError:
                    # can not move back
                    self.moved_to_end_count.add(track_name)

            if self._counter.get(codectools.text(i.name())) == 0:
                cleanups.append(_move_back)
            i.move(track_length)

        def _compat_end_items():
            out_max = max(i[1] for i in itervalues(self._m))
            end_items = (i for i in track.items() if i.timelineIn() > out_max)
            q = out_max
            for i in end_items:
                offset = q - i.timelineIn()
                assert offset < 0, "offset should be negative"
                i.move(offset + 1)
                q = i.timelineOut()

        cleanups.append(_compat_end_items)

        for i in reversed(track_items):
            _move_to_end(i)

        _counter = _NameCounter()
        for i in track_items:
            name = i.name().decode("utf-8")
            key = (name, _counter.add(name))
            times = self._m.get(key)
            if not times:
                self.ignored_count.add(track_name)
                continue
            i.setTimes(*times)
            self.aligned_count.add(track_name)

        # add missing items
        _existed_name = _NameCounter()
        _item_constructors = {}  # type: Dict[Text, Callable[[], hiero.core.TrackItem]]

        def _item_constructor_of(item):
            # type: (hiero.core.TrackItem) -> Callable[[], hiero.core.TrackItem]
            def _constructor():
                return item.copy()

            return _constructor

        for i in track_items:
            name = codectools.text(i.name())
            _existed_name.add(name)
            _item_constructors[name] = _item_constructor_of(i)
        for name, c_current in _existed_name.items():
            c_expected = self._counter.get(name)
            for c in range(1, c_expected + 1):
                if c <= c_current:
                    continue
                times = self._m[(name, c)]
                item = _item_constructors[name]()
                item.setTimes(*times)
                track.addTrackItem(item)
                self.created_count.add(track_name)

        while cleanups:
            cleanups.pop()()


def align_other_track_by(items):
    # type: (Iterator[hiero.core.TrackItem]) -> AlignPlan
    ap = AlignPlan()
    target_sequences = set()  # type: Set[hiero.core.Sequence]
    for i in items:
        s = i.sequence()
        assert s
        target_sequences.add(s)
        ap.add_base_item(i)
    for s in target_sequences:
        with s.project().beginUndo("align track items: %s" % s.name()):
            for t in s.videoTracks():
                ap.apply_to_track(t)
            for t in s.audioTracks():
                ap.apply_to_track(t)
    return ap


def remove_version_suffix(items):
    # type: (Iterator[hiero.core.TrackItem]) -> Dict[Text, Text]
    pattern = re.compile(r"^(.*)_v\d+$")
    result = {}  # type: Dict[Text, Text]
    for i in items:
        name = codectools.text(i.name())
        match = pattern.match(name)
        if not match:
            continue
        base = match.group(1)
        i.setName(codectools.binary(base))
        result[name] = base

    return result
