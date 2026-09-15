package com.uwords.usecase.port.auth.session;

import java.util.Map;

public interface AccessTokenDecoderPort {

    Map<String, Object> decode(String token);
}
