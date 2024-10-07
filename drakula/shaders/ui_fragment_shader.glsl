#version 330
uniform sampler2D pygame_texture;
uniform float iTime;
in vec2 uvs;
out vec4 fragColor;

float INTENSITY = 0.3+ sin(iTime * 6.0)+1;
float RADIUS = 1.5;

vec4 Glow(vec2 uv) {
    vec4 originalColor = texture(pygame_texture, uv);
    vec4 glowColor = vec4(0.0);
    float totalWeight = 0.0;

    for (float x = -RADIUS; x <= RADIUS; x++) {
        for (float y = -RADIUS; y <= RADIUS; y++) {
            vec2 offset = vec2(float(x), float(y)) / textureSize(pygame_texture, 0);
            vec4 sampleColor = texture(pygame_texture, uv + offset);

            if (sampleColor.g > 0.5 && sampleColor.r < 0.5 && sampleColor.b < 0.5) {
                float weight = 1.0 - length(vec2(x, y)) / float(RADIUS);
                glowColor += sampleColor * weight;
                totalWeight += weight;
            }
        }
    }

    if (totalWeight > 0.0) {
        glowColor /= totalWeight;
        glowColor *= INTENSITY;

        return max(originalColor, glowColor);
    }

    return originalColor;
}

void main() {
    fragColor = Glow(uvs);
}