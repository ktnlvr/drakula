#version 330
uniform sampler2D texture0;
uniform vec3 iResolution;
uniform float iTime;
uniform float iTimeDelta;
uniform int iFrame;
uniform vec4 iMouse;
uniform vec4 iDate;
in vec2 uvs;
out vec4 fragColor;

void mainImage(out vec4 fragColor, in vec2 fragCoord);

void main() {
    mainImage(fragColor, gl_FragCoord.xy);
}

//Start of shader
float Falloff = 0.3;

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
	vec2 uv = fragCoord.xy / iResolution.xy;
    vec4 pixel = texture(texture0, uvs);
    pixel = pixel.bgra;
    vec2 coord = (uv - 0.5) * (iResolution.x/iResolution.y) * 2.0;
    float rf = sqrt(dot(coord, coord)) * Falloff;
    float rf2_1 = rf * rf + 1.0;
    float e = 1.0 / (rf2_1 * rf2_1);

    vec4 src = vec4(1.0,1.0,1.0,1.0);
	fragColor = pixel * vec4(src.rgb * e, 0.5);
}