import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, "../../../..")))
from v1.lib.s3.rgw import Config
from v1.lib.s3.rgw import ObjectOps
import v1.lib.s3.rgw as rgw_lib
import v1.utils.log as log
import sys
from v1.utils.test_desc import AddTestInfo
import argparse
import yaml
import simplejson
from v1.lib.read_io_info import ReadIOInfo
from v1.lib.io_info import AddIOInfo

def test_exec(config):
    add_io_info = AddIOInfo()
    add_io_info.initialize()

    read_io = ReadIOInfo()

    test_info = AddTestInfo('multipart Upload')

    try:

        # test case starts

        test_info.started_info()

        with open('user_details') as fout:
            all_user_details = simplejson.load(fout)

        log.info('multipart upload enabled')

        for each_user in all_user_details:
            add_io_info.add_user_info(**{'user_id': each_user['user_id'],
                                         'access_key': each_user['access_key'],
                                         'secret_key': each_user['secret_key']})


        for each_user in all_user_details:

            config.objects_count = 1

            rgw = ObjectOps(config, each_user)
            buckets = rgw.create_bucket()

            rgw.multipart_upload(buckets)

        test_info.success_status('test completed')

        sys.exit(0)

    except AssertionError, e:
        log.error(e)
        test_info.failed_status('test failed: %s' % e)
        sys.exit(1)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='RGW Automation')

    parser.add_argument('-c', dest="config",
                        help='RGW Test yaml configuration')

    parser.add_argument('-p', dest="port", default='8080',
                        help='port number where RGW is running')

    args = parser.parse_args()

    yaml_file = args.config
    config = Config()
    config.port = args.port
    if yaml_file is None:
        config.bucket_count = 10
        config.objects_size_range = {'min': 300, 'max': 500}
    else:
        with open(yaml_file, 'r') as f:
            doc = yaml.load(f)
        config.bucket_count = doc['config']['bucket_count']
        config.objects_size_range = {'min': doc['config']['objects_size_range']['min'],
                                     'max': doc['config']['objects_size_range']['max']}

    log.info('bucket_count: %s\n'
             'object_min_size: %s\n'
             % (config.bucket_count, config.objects_size_range))

    test_exec(config)
