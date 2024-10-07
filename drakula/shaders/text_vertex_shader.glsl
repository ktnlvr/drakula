#version 330
in vec2 position;
out vec2 uvs;
void main() {
    gl_Position = vec4(position, 0.0, 1.0);
    uvs = (position + 1.0) * 0.5;
    uvs.y = 1.0 - uvs.y;
}