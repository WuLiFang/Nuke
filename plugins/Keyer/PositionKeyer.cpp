// PositionKeyerKernel
// VERSION: 0.5.0
kernel PositionKeyer : ImageComputationKernel<ePixelWise>
{
  Image<eRead, eAccessPoint, eEdgeClamped> position;
  Image<eWrite, eAccessPoint> dst;

param:
  bool invert_x;
  bool invert_y;
  bool invert_z;
  bool enable_x;
  bool enable_y;
  bool enable_z;
  int mode;
  float3 rotate;
  float3 scale;
  float4 p0_color;
  float4 p1_color;

local:
  float3 p0;
  float3 p1;

  float3 rotate3(float3 point, float3 rotate)
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
  float3 rotate3(float4 point, float3 rotate)
  {
    return rotate3(to_float3(point), rotate);
  }
  float linear(float x, float p0, float p1)
  {
    if (p1 == p0)
    {
      return p0;
    }
    return (x - p0) / (p1 - p0);
  }
  float3 to_float3(float4 input)
  {
    return float3(input.x, input.y, input.z);
  }
  void init()
  {
    p0 = rotate3(p0_color, rotate);
    p1 = rotate3(p1_color, rotate);
  }

  void process()
  {
    float3 pos = rotate3(position(), rotate);
    float4 result;

    if (mode == 0)
    {
      result[0] = linear(pos.x, p0.x, p1.x);
      result[1] = linear(pos.y, p0.y, p1.y);
      result[2] = linear(pos.z, p0.z, p1.z);
    }
    else if (mode == 1)
    {
      result[0] = 1 - fabs(pos.x - p1.x) / fabs(p1.x - p0.x) / scale.x;
      result[1] = 1 - fabs(pos.y - p1.y) / fabs(p1.y - p0.y) / scale.y;
      result[2] = 1 - fabs(pos.z - p1.z) / fabs(p1.z - p0.z) / scale.z;
    }
    else if (mode == 2)
    {
      float ret = 1 - length((pos - p1) / scale) / (length(p1 - p0));
      result[0] = ret;
      result[1] = ret;
      result[2] = ret;
    }
    result = clamp(result, float4(0.0f), float4(1.0f));
    result[0] = invert_x ? (1 - result[0]) : result[0];
    result[1] = invert_y ? (1 - result[1]) : result[1];
    result[2] = invert_z ? (1 - result[2]) : result[2];
    result[3] = (enable_x ? result[0] : 1) * (enable_y ? result[1] : 1) * (enable_z ? result[2] : 1);

    dst() = result;
  }
};
