FROM golang
RUN mkdir -p /workspace
WORKDIR /workspace
COPY main.go /workspace
COPY src /workspace/src
RUN go build main.go

EXPOSE 8080
CMD ["./main"]