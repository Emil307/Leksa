package com.uwords.adapter.cache;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;

public final class CacheScripts {

    public static final String RECORD_KEY_PREFIX_PLACEHOLDER = "{record_key_prefix}";
    public static final String POINTER_PREFIX_PLACEHOLDER = "{pointer_prefix}";
    public static final String POINTER_MIDDLE_PLACEHOLDER = "{pointer_middle}";
    public static final String POINTER_SUFFIX_PLACEHOLDER = "{pointer_suffix}";

    public static final String ACQUIRE_COOLDOWN = load("acquire-cooldown.lua");
    public static final String DISCARD_STARTED_CHALLENGE = load("discard-started-challenge.lua");
    public static final String SWAP_CHALLENGE = load("swap-challenge.lua")
            .replace(RECORD_KEY_PREFIX_PLACEHOLDER, CacheKeys.RECORD_KEY_PREFIX);
    public static final String CLAIM_ATTEMPT = load("claim-attempt.lua")
            .replace(POINTER_PREFIX_PLACEHOLDER, CacheKeys.POINTER_PREFIX)
            .replace(POINTER_MIDDLE_PLACEHOLDER, CacheKeys.POINTER_MIDDLE)
            .replace(POINTER_SUFFIX_PLACEHOLDER, CacheKeys.POINTER_SUFFIX);

    private CacheScripts() {
    }

    private static String load(String name) {
        String location = "/redis/" + name;
        try (InputStream source = CacheScripts.class.getResourceAsStream(location)) {
            if (source == null) {
                throw new IllegalStateException("Missing Redis script resource " + location);
            }
            return new String(source.readAllBytes(), StandardCharsets.UTF_8);
        } catch (IOException failure) {
            throw new UncheckedIOException(failure);
        }
    }
}
