FROM postgres:latest

COPY ./docker-entrypoint.sh .

RUN chmod +x /docker-entrypoint.sh

USER postgres

ENTRYPOINT [ "/docker-entrypoint.sh" ]

EXPOSE 5432
CMD ["postgres"]