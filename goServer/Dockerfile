FROM golang:1.21

WORKDIR /usr/src/app

# Add files
ADD . .

RUN go mod download

RUN go build /usr/src/app/server.go

EXPOSE 3333

CMD go run /usr/src/app/server.go