#!/bin/sh
exec /usr/bin/ssh -o StrictHostKeyChecking=no -i "${DIARY_ID_RSA}" "$@"
