package com.uwords.application;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.uwords")
public class UwordsApplication {

    public static void main(String[] args) {
        SpringApplication.run(UwordsApplication.class, args);
    }
}
