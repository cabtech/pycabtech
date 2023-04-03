"""module of functions for handling AWS activities"""
# -*- coding: utf-8 -*-
# pylint: disable-msg=line-too-long
# pylint: disable-msg=useless-return

import logging

# --------------------------------


def get_instance_name(instance: dict) -> str:
    """get an instance's tag:Name or its InstanceId"""
    tags = instance.get("Tags", [])
    return get_tag_by_key(tags, "Name", instance.get("InstanceId", "NoSuchInstance"))


def get_tag_by_key(tags: list, key: str, default: str) -> str:
    """look for a tag and return its value or a default"""
    for tag in tags:
        if tag["Key"] == key:
            return tag["Value"]
    return default


def has_tag(tags: list, key: str) -> bool:
    """see if the resource has a specific tag key"""
    for tag in tags:
        if tag["Key"] == key:
            return True
    return False


# --------------------------------
# instance functions


def get_instances(client, xargs=None):
    """returns a list of ec2 instances"""
    if xargs is None:
        reply = client.describe_instances()
    else:
        reply = client.describe_instances(**xargs)
    instances = []
    # num_res = 0
    for reservation in reply["Reservations"]:
        # num_res += 1
        for instance in reservation["Instances"]:
            instances.append(instance)
    # print('Loaded %d instances from %d reservations' % (len(instances), num_res,))
    return instances


def find_instance(instances, iid):
    """convenience function for returning an instance from a list"""
    return find_resource(instances, iid, "InstanceId")


def instance_exists(instances, iid):
    """convenience function for checking if an instance exists"""
    return resource_exists(instances, iid, "InstanceId")


def tbd_get_instance_name(instances, iid):
    """convenience function to find the tag:Name of an ec2 instance"""
    return get_resource_name(instances, iid, "InstanceId")


# --------------------------------
# volume functions


def volume_exists(volumes, vid):
    """convenience function for checking if an volume exists"""
    return resource_exists(volumes, vid, "VolumeId")


def find_volume(volumes, vid):
    """convenience function for returning an volume from a list"""
    return find_resource(volumes, vid, "VolumeId")


# --------------------------------
# pylint: disable-msg=too-many-branches


def describe(client, task, key, sub_key=None, xargs=None):
    """generic function for calling functions using pagination if possible"""
    params = {}
    reply = []

    if client.can_paginate(task):
        paginator = client.get_paginator(task)
        params = {"PaginationConfig": {"PageSize": 50}}
        if xargs is not None:
            params.update(xargs)

        page_iterator = paginator.paginate(**params)
        num_pages = 0
        for page in page_iterator:
            if sub_key is not None:
                for item in page[key]:
                    for sub_item in item[sub_key]:
                        reply.append(sub_item)
            else:
                for item in page[key]:
                    reply.append(item)
            num_pages += 1
    elif task == "describe_images":
        if xargs is None or "Owners" not in xargs:
            logging.error("Will not query for all images - need an Owner")
            num_pages = 0
        else:
            params.update(xargs)
            tmp = client.describe_images(**params)
            reply = tmp["Images"]
            num_pages = 1
    else:
        if xargs is not None:
            params.update(xargs)
        num_pages = 1
        tmp = getattr(client, task)(**params)
        try:
            reply = tmp[key]
        except KeyError:
            logging.error("KeyError for %s in %s", key, task)

    logging.info("%s returned %d items in %d pages", task, len(reply), num_pages)
    return reply


# pylint: enable-msg=too-many-branches

# --------------------------------
# resource functions


def resource_exists(resources, rid, key):
    """general function for checking if a resource exists in a list"""
    if resources is not None:
        for resource in resources:
            if rid == resource[key]:
                return True
    return False


def find_resource(resources, rid, key):
    """general function for returning a resource from a list"""
    if resources is not None:
        for resource in resources:
            if rid == resource[key]:
                return resource
    return None


def get_resource_name(resources, rid, key):
    """looks through a list of resources and tries to return the tag:Name of the first match"""
    if resources is None:
        return None
    for resource in resources:
        if rid == resource[key]:
            try:
                return None  # WIP get_tag_value(resource['Tags'], 'Name')
            except KeyError:
                pass
    return None


# --------------------------------
