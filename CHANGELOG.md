# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0-dev.1] - 2024-05-16

### Added

- Hashicorp Vault integration


## [1.0.0] - 2024-04-11

### Added

- An interface for Fidelius gateway repos and admins to fulfil
- A mock implementation of a Fidelius gateway repo and admin that use a 
  simple singleton dict to store (and share) data during runtime
- Unittests for the mock implementation
- Unittests for the Parameter Store implementation using LocalStack
- A Factory class to get different implementation classes
- Methods to delete parameters
- Config params for the `AwsParamStoreRepo` to use a custom AWS endpoint in 
  order to hook up to stuff like LocalStack for testing and such

### Changed

- The API a little bit so we're no longer backwards compatible (hence the 
  major version bump to 1.0.0)
- All config params can now be explicitly given to the `AwsParamStoreRepo` 
  in addition to being picked up from environment variables if not supplied


## [0.6.0] - 2024-04-05

### Changed

- Just a version number bump because 0.5.0 was yanked temporarily while 
  dealing with code dependent on certain internal default values in fidelius 
  0.4.0 that were removed


## [0.5.0] - 2024-04-05

### Changed

- The version and created a new release to trigger the CI/CD thingamajig!


## [0.5.0-beta.1] - 2024-04-05

### Added

- This entire Project
