import nuke
def nodePresetsStartup():
  nuke.setUserPreset("Grade", "Cache/EP15_MP_bottom", {'label': '\xe5\xba\x95\xe9\x83\xa8\xe5\x85\x89', 'mix': '0.7', 'indicators': '16', 'gl_color': '0xc232ff00', 'white': '1.889788151 0.09978818893 1.709788084 1', 'gamma': '1.7'})
  nuke.setUserPreset("Grade", "Cache/EP15_diffuse", {'whitepoint': '1.811523438 2.38671875 3.06640625 0.3728027344', 'white': '0.6 0.85 1.55 1', 'selected': 'true', 'note_font': '\xe5\xbe\xae\xe8\xbd\xaf\xe9\x9b\x85\xe9\xbb\x91', 'gl_color': '0xff363200'})
  nuke.setUserPreset("Grade", "Cache/EP15_GI", {'note_font': '\xe5\xbe\xae\xe8\xbd\xaf\xe9\x9b\x85\xe9\xbb\x91', 'whitepoint': '0.2071533203 0.2839355469 0.4118652344 1', 'selected': 'true', 'multiply': '0.33', 'gl_color': '0xff363200', 'white': '0.6 0.75 1.65 1'})
  nuke.setUserPreset("Grade", "Cache/EP15_specular", {'multiply': '0.3', 'whitepoint': '0.1809082031 0.2683105469 0.4260253906 1', 'white': '0.45 0.75 1.85 1', 'note_font': '\xe5\xbe\xae\xe8\xbd\xaf\xe9\x9b\x85\xe9\xbb\x91', 'gl_color': '0xff363200'})
  nuke.setUserPreset("Grade", "Cache/EP15_SSS", {'note_font': '\xe5\xbe\xae\xe8\xbd\xaf\xe9\x9b\x85\xe9\xbb\x91', 'whitepoint': '0.53515625 0.4833984375 0.4733886719 1', 'selected': 'true', 'multiply': '0.35', 'gl_color': '0x9332ff00', 'white': '0.9 0.85 1.25 1'})
