ARG BUILD_FROM
FROM $BUILD_FROM

# Install postgresql-client
RUN apk add --no-cache postgresql-client jq

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
