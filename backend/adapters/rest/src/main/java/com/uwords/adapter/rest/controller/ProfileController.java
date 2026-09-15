package com.uwords.adapter.rest.controller;

import com.uwords.adapter.rest.dto.profile.UserProfileResponseDto;
import com.uwords.domain.auth.user.User;
import com.uwords.usecase.AuthenticatedCaller;
import com.uwords.usecase.service.profile.ReadUserProfileService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ProfileController {

    private final ReadUserProfileService profileService;

    public ProfileController(ReadUserProfileService profileService) {
        this.profileService = profileService;
    }

    @GetMapping(RestPaths.PROFILE_PATH)
    public ResponseEntity<UserProfileResponseDto> readProfile(AuthenticatedCaller caller) {
        User user = profileService.read(caller);
        return ResponseEntity.ok(UserProfileResponseDto.from(user));
    }
}
