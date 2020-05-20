# Module Guide

A Katana module is any target, or tool, or supporting service that is under the management of Katana.

## Attributes
- name
- description
- category
- provisioner
- href
- is-runnable
- depends-on

## Dependencies
A module may be dependent on other modules. In this case, the following rules apply:

1. Installing a dependent module will first install its dependencies.
2. Starting a dependent module will first start its dependencies.

Dependencies are listed under the _depends-on_ attribute.

## Actions
- Install
- Remove
- Start
- Stop
- Status

## Status
- running
- stopped
- installed
- changing
- not installed
- blocked - a dependency status is preventing the read of this status
- unknown - an unexpected error is preventing the read of the status
