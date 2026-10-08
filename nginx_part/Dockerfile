FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
   --no-install-recommends  nginx \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["nginx", "-g", "daemon off;"]

yc compute instance create-with-container \
  --name devops-vm \
  --zone ru-central1-b \
  --ssh-key ~/.ssh/id_ed25519.pub \
  --service-account-name devopser \
  --create-boot-disk size=30 \
  --public-ip \
  --platform standard-v3 \
  --container-name=ngi \
  --container-image=cr.yandex/crponldup29rv8392rjb/ubuntu-nginx