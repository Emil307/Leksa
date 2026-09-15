package com.uwords.adapter.cache;

import java.util.UUID;

public final class CacheKeys {

    public static final String CHALLENGE_ID_PLACEHOLDER = "{challenge_id}";
    public static final String CHALLENGE_TYPE_PLACEHOLDER = "{challenge_type}";
    public static final String UNIQUENESS_KEY_PLACEHOLDER = "{uniqueness_key}";

    public static final String RECORD_KEY = "challenge:" + CHALLENGE_ID_PLACEHOLDER;
    public static final String POINTER_KEY =
            "challenge:key:" + CHALLENGE_TYPE_PLACEHOLDER + ":" + UNIQUENESS_KEY_PLACEHOLDER;
    public static final String COOLDOWN_KEY =
            "challenge:cooldown:" + CHALLENGE_TYPE_PLACEHOLDER + ":" + UNIQUENESS_KEY_PLACEHOLDER;
    public static final String VERIFICATION_KEY = "challenge:verified:" + CHALLENGE_ID_PLACEHOLDER;

    public static final String POINTER_PREFIX = before(POINTER_KEY, CHALLENGE_TYPE_PLACEHOLDER);
    public static final String POINTER_MIDDLE =
            before(after(POINTER_KEY, CHALLENGE_TYPE_PLACEHOLDER), UNIQUENESS_KEY_PLACEHOLDER);
    public static final String POINTER_SUFFIX =
            after(after(POINTER_KEY, CHALLENGE_TYPE_PLACEHOLDER), UNIQUENESS_KEY_PLACEHOLDER);
    public static final String RECORD_KEY_PREFIX = RECORD_KEY.replace(CHALLENGE_ID_PLACEHOLDER, "");

    private CacheKeys() {
    }

    public static String recordKey(UUID challengeId) {
        return RECORD_KEY.replace(CHALLENGE_ID_PLACEHOLDER, challengeId.toString());
    }

    public static String verificationKey(UUID challengeId) {
        return VERIFICATION_KEY.replace(CHALLENGE_ID_PLACEHOLDER, challengeId.toString());
    }

    public static String pointerKey(String challengeType, String uniquenessKey) {
        return POINTER_KEY
                .replace(CHALLENGE_TYPE_PLACEHOLDER, challengeType)
                .replace(UNIQUENESS_KEY_PLACEHOLDER, uniquenessKey);
    }

    public static String cooldownKey(String challengeType, String uniquenessKey) {
        return COOLDOWN_KEY
                .replace(CHALLENGE_TYPE_PLACEHOLDER, challengeType)
                .replace(UNIQUENESS_KEY_PLACEHOLDER, uniquenessKey);
    }

    private static String before(String template, String placeholder) {
        return template.substring(0, template.indexOf(placeholder));
    }

    private static String after(String template, String placeholder) {
        return template.substring(template.indexOf(placeholder) + placeholder.length());
    }
}
