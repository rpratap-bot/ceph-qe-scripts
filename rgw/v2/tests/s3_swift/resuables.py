import os, sys

sys.path.append(os.path.abspath(os.path.join(__file__, "../../../..")))
import v2.lib.resource_op as s3lib
import v2.utils.log as log
import v2.utils.utils as utils
from v2.utils.utils import HttpResponseParser
from v2.lib.exceptions import TestExecError
import v2.lib.manage_data as manage_data


def create_bucket(bucket_name, rgw, user_info):
    log.info('creating bucket with name: %s' % bucket_name)
    # bucket = s3_ops.resource_op(rgw_conn, 'Bucket', bucket_name_to_create)
    bucket = s3lib.resource_op({'obj': rgw,
                                'resource': 'Bucket',
                                'args': [bucket_name]})
    created = s3lib.resource_op({'obj': bucket,
                                 'resource': 'create',
                                 'args': None,
                                 'extra_info': {'access_key': user_info['access_key']}})
    if created is False:
        raise TestExecError("Resource execution failed: bucket creation faield")
    if created is not None:
        response = HttpResponseParser(created)
        if response.status_code == 200:
            log.info('bucket created')
        else:
            raise TestExecError("bucket creation failed")
    else:
        raise TestExecError("bucket creation failed")
    return bucket


def upload_object(s3_object_name, bucket, TEST_DATA_PATH, config, user_info, append_data=False, append_msg=None):
    log.info('s3 object name: %s' % s3_object_name)
    s3_object_path = os.path.join(TEST_DATA_PATH, s3_object_name)
    log.info('s3 object path: %s' % s3_object_path)
    s3_object_size = utils.get_file_size(config.objects_size_range['min'],
                                         config.objects_size_range['max'])
    if append_data is True:
        data_info = manage_data.io_generator(s3_object_path, s3_object_size, data='append',
                                             **{'message': '\n%s' % append_msg})
    else:
        data_info = manage_data.io_generator(s3_object_path, s3_object_size)
    if data_info is False:
        TestExecError("data creation failed")
    log.info('uploading s3 object: %s' % s3_object_path)
    upload_info = dict({'access_key': user_info['access_key']}, **data_info)
    object_uploaded_status = s3lib.resource_op({'obj': bucket,
                                                'resource': 'upload_file',
                                                'args': [s3_object_path, s3_object_name],
                                                'extra_info': upload_info})
    if object_uploaded_status is False:
        raise TestExecError("Resource execution failed: object upload failed")
    if object_uploaded_status is None:
        log.info('object uploaded')


def enable_versioning(bucket, rgw_conn, user_info, write_bucket_io_info):
    log.info('bucket versionig test on bucket: %s' % bucket.name)
    # bucket_versioning = s3_ops.resource_op(rgw_conn, 'BucketVersioning', bucket.name)
    bucket_versioning = s3lib.resource_op({'obj': rgw_conn,
                                           'resource': 'BucketVersioning',
                                           'args': [bucket.name]})
    # checking the versioning status
    # version_status = s3_ops.resource_op(bucket_versioning, 'status')
    version_status = s3lib.resource_op({'obj': bucket_versioning,
                                        'resource': 'status',
                                        'args': None
                                        })
    if version_status is None:
        log.info('bucket versioning still not enabled')
    # enabling bucket versioning
    # version_enable_status = s3_ops.resource_op(bucket_versioning, 'enable')
    version_enable_status = s3lib.resource_op({'obj': bucket_versioning,
                                               'resource': 'enable',
                                               'args': None})
    response = HttpResponseParser(version_enable_status)
    if response.status_code == 200:
        log.info('version enabled')
        write_bucket_io_info.add_versioning_status(user_info['access_key'], bucket.name,
                                                   'enabled')
    else:
        raise TestExecError("version enable failed")
