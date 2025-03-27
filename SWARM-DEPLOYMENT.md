

# Swarm Deployment

The main difference between a `localhost` deployment and a `swarm` deployment is that there are multiple compute nodes where various components can be deployed to. Another key difference is that ccomponents are added as a service where each can be configure with multiple scalability configurations and other service options.

## clusters

![Swarm](./docs/images/swarm.png)

As show above at the minimum there is a cluster of four compute instances, labeled `platform`, `db`, `agent`, and `service`. 

The mapping various components to the compute cluster is done through deployment constraints (see below swarm setup). In the current setup the cluster has nodes with labels: db, platform, agent, and service. Redis container is deployed on the db nodes, API and frontend deployed on the platform node,  agent containers are deployed to the agent node, and finally any service that can be used by agents is deployed on service node. Communication between the various components is done through an overlay network dedicated to the plaform. The overlay network enables easy communication among components with components simply reachable through their service names (see https://docs.docker.com/network/drivers/overlay/)

For larger deployments and complex scenarios, multiple nodes can be designated to each function, and one can introduce different labels to define complex deployment targets.

Each deployment of the platform is named, with a separate network so that each component in the platform is addressible using the same hostname within its specific network.

## requirements

As in the `localhost` deployment mode, the production of Blue also requires docker engine to build and run the infrastructure and agents. In addition, docker swarm is used for creating a production infrastructure and docker hub is used as a repository of docker images.

  
## setup

### swarm setup

First, you need to create multiple compute (e.g. AWS EC2) instances. For this step, please refer to your cloud providers documentation. For AWS, you can find it here: https://aws.amazon.com/ec2/getting-started/. In addition, to allow some easy data sharing you can create a filesystem to share among the compute instances. For AWS EFS, refer to: https://aws.amazon.com/efs/getting-started/. 

Once you have several compute instances, you can build a swarm consisting of manager and worker nodes. As part of blue platform scripts, we have convenience scripts to help you initiate a swarm, add nodes, and label them for blue deployments. For more details on swarm you can read: https://docs.docker.com/engine/swarm/

To initiate a swarm, run below command on the designated manager node:
```
$ cd platform/scripts
$ ./init_swarm.sh /mnt/efs/fs1/blue_swarm
```

Once completed, you will have the manager and worker tokens saved as `.manager.token` and `.worker.token`.  You can then use to go to other compute instances and join the swarm. You can either copy these files or share them via shared filesystem:

Before running below commands make sure `.manager.token` and `.worker.token` files are transferred and are in the same directory.

To join as worker, run:
```
$ cd platform/scripts
$ ./join_swarm.sh worker /mnt/efs/fs1/blue_swarm
```
To join as manager run `./joinswarm.sh manager`. To leave swarm run `./leave_swarm.sh`

Once all nodes are in the swarm, label them so that when blue is deployed they go to the appropriate node. Blue uses by default four labels: `platform`, `db`, `agent` and `service`

For each node label them with one of the above labels:
```
$ cd platform/scripts
# ./add_label.sh <label> <node>
```
where <label> is either `platform`, `db`, `agent` or `service` and <node> is the node id when you run `docker node ls`.

### data volume setup

For the swarm mode it is best to utilize a shared filesystem as the location of the data folder. Set `BLUE_DATA_DIR` to a folder on such a shared filesystem. Next, to create a data volume, run:

```
$ cd platform/scripts
$ ./create_data_volume.sh --platform default
```

This will create a directory called default under the $BLUE_DATA_DIR directory, and create a volume on that directory.

## build / publish

Beyond building docker images for agents and platform componens, as in the `localhost` mode, in the `swarm` mode the images need to be published to docker hub. To do so, once built, you need to run publish scriips.

For example, to publish all agent images:
```
$ cd agents
$ ./docker_publish_all_agents.sh
```

Likewise, for API and frontend run their respective scriipts, `docker_publish_api.sh` and `docker_publish_frontend.sh` in their directories.

## deployment

To deploy blue on a swarm, with the default options, run:
```
$ cd platform/scripts
$ ./deploy_platform.sh --target swarm
```

To test your deployment you can run:
```
$ docker service ls
```

and the list should contain three services running: redis, api , and frontend

If you want to see it in action on the web, you can bring up the frontend by browsing to `http://<platform_ip_address>:3000` and the API documentation on `http://<platform_ip_address>:5050/docs#/`

</br>