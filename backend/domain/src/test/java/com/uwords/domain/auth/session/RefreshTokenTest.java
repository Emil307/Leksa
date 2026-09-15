package com.uwords.domain.auth.session;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;

class RefreshTokenTest {

    private static final String SENTINEL = "SENTINEL-refresh-token-9f2c";

    @Test
    void shouldRenderOnlyTheRedactionMarkerInsteadOfTheValue() {
        RefreshToken token = RefreshToken.of(SENTINEL);

        String rendered = token.toString();

        assertThat(rendered).isEqualTo("<redacted>").doesNotContain(SENTINEL);
    }
}
