#version 330
uniform sampler2D pygame_texture;
in vec2 uvs;
out vec4 fragColor;

void main() {
    fragColor = texture(pygame_texture, uvs);
}