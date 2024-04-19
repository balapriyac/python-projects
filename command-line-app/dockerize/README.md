## Get Started

Here are a couple of things you may want to do after you've [installed Docker](https://docs.docker.com/engine/install/) on your machine.

1. The Docker daemon binds to a Unix socket, owned by the `root` user by default. So you can access it only using `sudo`. To avoid prefixing all your docker commands with `sudo`, create a `docker` group and add user to group like so:

```sh
$ sudo groupadd docker
$ sudo usermod -aG docker $USER
```

2. If you use an older version of Docker, you may get deprecation warnings when you run the `docker build` command. This is because the legacy build client will be deprecated in future releases. So you may want to [install buildx](https://github.com/docker/buildx), a CLI tool to use BuildKit's capabilities. And use the `docker buildx build` command to build with BuildKit.

## Build and Run the Docker Image

Here we containerize a simple [command-line TODO list app](https://github.com/balapriyac/python-projects/blob/main/command-line-app/dockerize/todo.py) with Docker. To build an image from the [Dockerfile](https://github.com/balapriyac/python-projects/blob/main/command-line-app/dockerize/Dockerfile) run:

```sh
docker build todo-app .
```

And start the container (we need an interactive terminal session within the container) by running the following `docker run` command:

```sh
docker run -it todo-app
```
