#version 330

in vec2 position;
out vec2 uvs;
out vec2 worldPos;

void main() {
    uvs = (position + 1.0) * 0.5;
    uvs.y = 1.0 - uvs.y;

     worldPos = vec2(
        mix(-180.0, 180.0, uvs.x),
        mix(-90.0, 90.0, uvs.y)
    );

    gl_Position = vec4(position, 0.0, 1.0);
}
