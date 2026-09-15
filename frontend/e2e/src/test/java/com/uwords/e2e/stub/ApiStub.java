package com.uwords.e2e.stub;

import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

public final class ApiStub {

    private static final String PORT_ENV = "E2E_API_STUB_PORT";
    private static ApiStub instance;

    private final ChallengeStore store = new ChallengeStore();
    private final ChallengeHandler handler = new ChallengeHandler(store);

    private ApiStub() throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(requirePort()), 0);
        server.createContext("/", this::serve);
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();
    }

    public static synchronized ApiStub instance() {
        if (instance == null) {
            try {
                instance = new ApiStub();
            } catch (IOException e) {
                throw new IllegalStateException("Cannot start API stub on port from " + PORT_ENV, e);
            }
        }
        return instance;
    }

    public ChallengeStore store() {
        return store;
    }

    private void serve(HttpExchange exchange) throws IOException {
        addCorsHeaders(exchange);
        if ("OPTIONS".equals(exchange.getRequestMethod())) {
            exchange.sendResponseHeaders(204, -1);
            exchange.close();
            return;
        }
        String rawBody = new String(exchange.getRequestBody().readAllBytes(), StandardCharsets.UTF_8);
        StubResponse response = handler.handle(exchange.getRequestMethod(), exchange.getRequestURI().getPath(), rawBody);
        byte[] bytes = response.body().getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().add("Content-Type", "application/json");
        exchange.sendResponseHeaders(response.status(), bytes.length);
        try (OutputStream out = exchange.getResponseBody()) {
            out.write(bytes);
        }
    }

    private static void addCorsHeaders(HttpExchange exchange) {
        exchange.getResponseHeaders().add("Access-Control-Allow-Origin", "*");
        exchange.getResponseHeaders().add("Access-Control-Allow-Headers", "Content-Type");
        exchange.getResponseHeaders().add("Access-Control-Allow-Methods", "POST, GET, OPTIONS");
    }

    private static int requirePort() {
        String port = System.getenv(PORT_ENV);
        if (port == null || port.isBlank()) {
            throw new IllegalStateException(PORT_ENV + " is required; run via frontend/infrastructure/scripts/test-e2e.sh");
        }
        return Integer.parseInt(port.trim());
    }
}
