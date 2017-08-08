// PositionKeyerKernel
// VERSION: 0.31
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

  float4 rotate3(float4 pos, float ry)
  {
    float4 ret;
    ret[0] = cos(ry) * pos[2] - sin(ry) * pos[0];
    ret[1] = pos[1];
    ret[2] = cos(ry) * pos[0] + sin(ry) * pos[2];
    return ret;
  }

  float2 rotate2(float a, float b, float angle)
  {
    float2 ret;
    ret[0] = cos(angle) * b - sin(angle) * a;
    ret[1] = cos(angle) * a + sin(angle) * b;
    return ret;
  }
  float linear(float x, float p0, float p1)
  {
    return (x - p0) / (p1 - p0);
  }

  void init()
  {
    p0 = rotate3(p0_color, rotate_y);
    p1 = rotate3(p1_color, rotate_y);
  }

  void process()
  {
    float4 pos = rotate3(position(), rotate_y);
    const float x = pos[0];
    const float y = pos[1];
    const float z = pos[2];

    float4 result;
    result[0] = linear(x, p0[0], p1[0]);
    result[1] = linear(y, p0[1], p1[1]);
    result[2] = linear(z, p0[2], p1[2]);
    result = clamp(result, float4(0.0f), float4(1.0f));

    result[0] = invert_x ? (1 - result[0]) : result[0];
    result[1] = invert_y ? (1 - result[1]) : result[1];
    result[3] = (enable_x ? result[0] : 1) * (enable_y ? result[1] : 1);

    dst() = result;
  }
};