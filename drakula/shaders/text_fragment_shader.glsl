#version 330
uniform sampler2D text_texture;
in vec2 uvs;
out vec4 fragColor;

void main() {
    fragColor = texture(text_texture, uvs);
}