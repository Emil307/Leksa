package com.uwords.e2e.stub;

import java.util.Map;

public record RecordedRequest(String method, String path, Map<String, Object> body) {
}
