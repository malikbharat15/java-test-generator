"""
gRPC Service Smoke Test Prompt

Specializes in generating smoke tests for gRPC services.
"""

GRPC_PROMPT = """
SPECIALIZATION: gRPC Service Smoke Tests
========================================

TEST APPROACH:
- Use grpcurl or gRPC client stubs
- Test health check service (if available)
- Invoke simple RPC methods
- Verify service is reachable and responding

NEWMAN WORKAROUND (HTTP/2):
- If gRPC-Web enabled, can use Postman
- Otherwise, generate shell script with grpcurl commands

JUNIT + gRPC Client APPROACH:
```java
@Test
void testGrpcServiceHealthCheck() {
    ManagedChannel channel = ManagedChannelBuilder
        .forAddress(grpcHost, grpcPort)
        .usePlaintext()
        .build();
    
    try {
        HealthGrpc.HealthBlockingStub healthStub = 
            HealthGrpc.newBlockingStub(channel);
        
        HealthCheckResponse response = healthStub.check(
            HealthCheckRequest.newBuilder()
                .setService("")
                .build()
        );
        
        assertEquals(ServingStatus.SERVING, response.getStatus());
    } finally {
        channel.shutdown();
    }
}
```

GRPCURL SCRIPT:
```bash
#!/bin/bash
# Smoke test gRPC service health
grpcurl -plaintext ${GRPC_HOST}:${GRPC_PORT} grpc.health.v1.Health/Check
exit $?
```

DETECTION:
- Look for @GrpcService annotation
- Check for grpc-spring-boot-starter, grpc-stub dependencies
- Find io.grpc imports
"""

def get_grpc_prompt():
    return GRPC_PROMPT
