import os, sys
sys.path.append(os.path.abspath(os.path.join(__file__, "../../..")))
from lib.s3.rgw import RGWMultpart
import utils.log as log
import sys
from utils.test_desc import AddTestInfo


def test_exec():

    test_info = AddTestInfo('Multi Part Upload and cancel after upload')

    try:

        test_info.started_info()

        rgw = RGWMultpart('2D6OA0XPW2WEY4LZND4T', '58onUujPfEJGmC8VVM9BHGq9SkC9vyeRZYAGp8AD')
        rgw.set_cancel_multipart = True

        rgw.upload(3000, 'third_large_bucket')

        test_info.success_status('test completed')

        sys.exit(0)

    except AssertionError, e:
        log.error(e)
        test_info.failed_status('test faield: %s' % e)
        sys.exit(1)


if __name__ == '__main__':
    test_exec()
