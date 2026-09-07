# SIPp_via_Python
SIPp controlled by Python to automate call flows


# SIP Test Automation PoC

A small, containerized SIP test automation proof of concept using **Python, SIPp, Asterisk, and Docker Compose**.

The purpose of this project is to demonstrate a clean separation between **test orchestration**, **SIP protocol execution**, and the **System Under Test (SUT)**.

## Architecture

```text
                         Test Orchestration
                                │
                                ▼
                         ┌─────────────┐
                         │   Python    │
                         │  runner.py  │
                         └──────┬──────┘
                                │
                         subprocess.run()
                                │
                                ▼
                         ┌─────────────┐
                         │    SIPp     │
                         │ SIP Engine  │
                         └──────┬──────┘
                                │
                         SIP / UDP 5060
                                │
                                ▼
                         ┌─────────────┐
                         │  Asterisk   │
                         │     SUT     │
                         │   PJSIP     │
                         └─────────────┘
```

### Component responsibilities

| Component      | Responsibility                          |
| -------------- | --------------------------------------- |
| Python         | Test orchestration and result reporting |
| SIPp           | SIP protocol execution                  |
| XML scenario   | Defines the SIP test sequence           |
| Asterisk       | System Under Test                       |
| Docker Compose | Reproducible test environment           |

Python does not implement SIP. It launches SIPp as an external process and consumes its output and exit code.

## Current Test Case

The initial test validates SIP REGISTER authentication using SIP Digest authentication.

```text
SIPp                         Asterisk
 │                              │
 │──── REGISTER ───────────────>│
 │                              │
 │<─── 401 Unauthorized ────────│
 │                              │
 │──── REGISTER + Digest ──────>│
 │                              │
 │<─── 200 OK ──────────────────│
 │                              │
```

Expected result:

```text
REGISTER ---------->  1
401 <----------      1
REGISTER ---------->  1
200 <----------      1

Successful call: 1
Failed call:     0
```

The Python test runner converts the SIPp process exit code into a test result:

```text
SIPp exit code 0  → PASS
SIPp exit code != 0 → FAIL
```

## Project Structure

```text
sip-poc/
├── README.md
├── docker-compose.yml
│
├── asterisk/
│   ├── pjsip.conf
│   └── extensions.conf
│
└── tester/
    ├── Dockerfile
    ├── runner.py
    └── scenarios/
        └── register.xml
```

## Requirements

* Docker
* Docker Compose

No local installation of Asterisk, SIPp, or Python is required.

## Running the PoC

Start Asterisk:

```bash
docker compose up -d asterisk
```

Run the test:

```bash
docker compose run --rm tester
```

The tester container is intentionally ephemeral. It is created for the test execution and removed after the test completes.

Expected output:

```text
Running test: REGISTER user 1001

============================================================
TEST:   REGISTER user 1001
RESULT: PASS
EXIT:   0
============================================================
```

## Asterisk CLI

An interactive Asterisk console can be opened with:

```bash
docker exec -it sip-poc-asterisk asterisk -rvvv
```

Useful commands:

```text
pjsip show endpoints
pjsip show transports
pjsip set logger on
```

Disable SIP logging with:

```text
pjsip set logger off
```

## SIP Packet Capture

SIP traffic can be captured from the Asterisk container using `tcpdump`.

For example:

```bash
docker exec sip-poc-asterisk tcpdump \
  -i any \
  -nn \
  -s 0 \
  -w /tmp/register.pcap \
  udp port 5060
```

The resulting capture can be inspected with Wireshark.

The expected SIP exchange is:

```text
REGISTER
   │
   ▼
401 Unauthorized
   │
   ▼
REGISTER + Authorization
   │
   ▼
200 OK
```

## Container Networking

The PoC currently uses Docker Compose with the tester sharing the Asterisk network namespace:

```yaml
network_mode: "service:asterisk"
```

This allows the SIPp process to reach Asterisk through:

```text
127.0.0.1:5060
```

The approach is intentionally simple for the initial proof of concept and removes unnecessary networking variables while validating the SIP automation architecture.

## Design Principles

The PoC intentionally separates responsibilities:

### Python — Orchestration

Python starts the test execution, invokes SIPp, captures its output, evaluates the exit code, and reports PASS/FAIL.

### SIPp — Protocol Execution

SIPp is responsible for generating and validating SIP messages according to the XML scenario.

### XML — Test Definition

The SIP scenario is kept outside the Python code.

This makes it possible to add additional SIP scenarios without embedding SIP message logic into the Python test runner.

### Asterisk — System Under Test

Asterisk provides a reproducible SIP endpoint and authentication service for the automated tests.

## Why Containerize the Environment?

Containerization provides:

* Reproducible test environments
* Isolation from the host system
* Consistent dependencies
* Easy setup and teardown
* Suitable integration with CI/CD pipelines

The tester image contains the required Python runtime and SIPp installation, while Asterisk is provided as a containerized SUT.

## Current Status

**PoC validated.**

The complete automated REGISTER authentication flow has been successfully executed:

```text
Python
  ↓
SIPp
  ↓
REGISTER
  ↓
Asterisk
  ↓
401
  ↓
SIPp Digest authentication
  ↓
REGISTER
  ↓
Asterisk
  ↓
200 OK
  ↓
Python
  ↓
PASS
```

## Future Improvements

Potential next steps include:

* Additional SIP call-flow scenarios
* INVITE / 180 Ringing / 200 OK / ACK / BYE testing
* Multiple test cases
* Test configuration externalization
* Structured test reporting
* JUnit XML output for CI/CD integration
* SIP trace artifact collection
* Automated packet capture
* CI pipeline integration
* Separation of test execution and reporting layers
* Optional executor/adapter abstraction for other protocol engines

The initial PoC deliberately keeps the architecture simple before introducing additional integration layers.

