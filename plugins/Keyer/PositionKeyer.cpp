// PositionKeyerKernel
// VERSION: 0.4.3
kernel PositionKeyer : ImageComputationKernel<ePixelWise>
{
  Image<eRead, eAccessPoint, eEdgeClamped> position;
  Image<eWrite, eAccessPoint> dst;

param:
  bool invert_x;
  bool invert_y;
  bool enable_x;
  bool enable_y;
  float3 rotate;
  float4 p0_color;
  float4 p1_color;

local:
  float4 p0;
  float4 p1;

  float4 rotate3(float4 point, float3 rotate)
  {
    float sx = sin(rotate.x);
    float cx = cos(rotate.x);
    float sy = sin(rotate.y);
    float cy = cos(rotate.y);
    float sz = sin(rotate.z);
    float cz = cos(rotate.z);
    float xy, xz, yx, yz, zx, zy;
    xy = cx * point.y - sx * point.z;
    xz = sx * point.y + cx * point.z;
    yx = cy * point.x - sy * xz;
    yz = sy * point.x + cy * xz;
    zx = cz * yx - sz * xy;
    zy = sz * yx + cz * xy;
    point.x = zx;
    point.y = zy;
    point.z = yz;
    return point;
  }

  float linear(float x, float p0, float p1)
  {
    if (p1 == p0){
      return p0;
    }
    return (x - p0) / (p1 - p0);
  }

  void init()
  {
    p0 = rotate3(p0_color, rotate);
    p1 = rotate3(p1_color, rotate);
  }

  void process()
  {
    float4 pos = rotate3(position(), rotate);

    float4 result;
    result[0] = linear(pos[0], p0[0], p1[0]);
    result[1] = linear(pos[1], p0[1], p1[1]);
    result[2] = linear(pos[2], p0[2], p1[2]);
    result = clamp(result, float4(0.0f), float4(1.0f));

    result[0] = invert_x ? (1 - result[0]) : result[0];
    result[1] = invert_y ? (1 - result[1]) : result[1];
    result[3] = (enable_x ? result[0] : 1) * (enable_y ? result[1] : 1);

    dst() = result;
  }
};