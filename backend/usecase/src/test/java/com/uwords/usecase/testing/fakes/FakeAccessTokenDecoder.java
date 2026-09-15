package com.uwords.usecase.testing.fakes;

import com.uwords.domain.auth.failure.AuthFailureReason;
import com.uwords.domain.auth.failure.Unauthorized;
import com.uwords.usecase.port.auth.session.AccessTokenDecoderPort;
import java.util.HashMap;
import java.util.Map;

public class FakeAccessTokenDecoder implements AccessTokenDecoderPort {

    public final Map<String, Map<String, Object>> claims = new HashMap<>();

    @Override
    public Map<String, Object> decode(String token) {
        Map<String, Object> found = claims.get(token);
        if (found == null) {
            throw Unauthorized.of(AuthFailureReason.SIGNATURE);
        }
        return found;
    }
}
