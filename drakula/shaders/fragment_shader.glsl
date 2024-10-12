#version 330

uniform sampler2D dayTexture;
uniform sampler2D nightTexture;
uniform float day;
uniform float daytime;
uniform vec3 iResolution;
uniform float iTime;
uniform float horizontalScroll;

in vec2 uvs;
in vec2 worldPos;
out vec4 fragColor;

const float PI = 3.14159265359;
float Falloff = 0.3;

float deg2rad(float degrees) {
    return degrees * PI / 180.0;
}

vec2 getSubsolarPoint() {
    float declination = 23.45 * (2 * atan(sin(deg2rad((360.0/365.0) * (day - 81)))) / PI + 1);
    float subsolarLong = 15.0 * (12.0 - daytime * (iTime/24));
    return vec2(subsolarLong, declination);
}

float getDaylight(vec2 worldCoord, vec2 subsolarPoint) {
    float lambda = deg2rad(worldCoord.x);
    float phi = deg2rad(worldCoord.y);
    float lambdaSs = deg2rad(subsolarPoint.x);
    float phiSs = deg2rad(subsolarPoint.y);

    float ha = lambda - lambdaSs;
    float tanPhi = -cos(ha) / tan(phiSs);
    float terminator = atan(tanPhi);

    return smoothstep(-0.15, 0.15, phi - terminator);
}

void main() {
    vec2 scrolledUV = vec2(mod(uvs.x - horizontalScroll, 1.0), uvs.y);
    vec2 scrolledWorld = vec2(mod(worldPos.x - horizontalScroll * 360.0, 360.0), worldPos.y);

    vec2 subsolarPoint = getSubsolarPoint();
    float daylight = getDaylight(scrolledWorld, subsolarPoint);

    vec4 dayColor = texture(dayTexture, scrolledUV);
    vec4 nightColor = texture(nightTexture, scrolledUV);

    vec4 mixedColor = mix(nightColor, dayColor, daylight);

    // Vignette effect
    vec2 coord = (scrolledUV - 0.5) * (iResolution.x/iResolution.y) * 2.0;
    float rf = sqrt(dot(coord, coord)) * Falloff;
    float rf2_1 = rf * rf + 1.0;
    float e = 1.0 / (rf2_1 * rf2_1);

    fragColor = mixedColor * vec4(e, e, e, 1.0);
}