#ifdef GL_ES
precision highp float;
#endif

uniform float u_time;
uniform vec2 u_resolution;

#define ITERATIONS 128

vec2 complex_square(vec2 v) {
    return vec2(
        v.x * v.x - v.y * v.y,
        v.x * v.y * 2.0
    );
}

void main() {
    vec2 uv = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
    
    // Animate the zoom and the seed point
    float zoom = 1.5 + sin(u_time * 0.1) * 0.5;
    vec2 c = vec2(-0.8 + sin(u_time * 0.2) * 0.05, 0.156 + cos(u_time * 0.3) * 0.05);
    
    vec2 z = uv * zoom;
    int iter = 0;
    
    for(int i = 0; i < ITERATIONS; i++) {
        z = complex_square(z) + c;
        if(dot(z, z) > 4.0) break;
        iter++;
    }
    
    // Color based on iterations
    float t = float(iter) / float(ITERATIONS);
    vec3 col = vec3(0.0);
    
    if (iter < ITERATIONS) {
        col = 0.5 + 0.5 * cos(3.0 + t * 20.0 + u_time + vec3(0.0, 0.6, 1.0));
    }
    
    gl_FragColor = vec4(col, 1.0);
}
