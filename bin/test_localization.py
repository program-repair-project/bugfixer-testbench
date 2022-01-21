#!/usr/bin/env python3

import argparse
import subprocess
import os
import logging
from datetime import datetime

PROJECT_HOME = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
RUN_DOCKER_SCRIPT = os.path.join(PROJECT_HOME, 'bin/run-docker.py')
OUT_DIR = os.path.join(PROJECT_HOME, 'localizer-outs')
ENGINE_LIST = ('tarantula', 'prophet', 'ochiai', 'jaccard')
bug_dict = {}
timestamp = ''

except_case_list = (  # build failure cases list
    '2011-01-06-e7a1d5004e-3571c955b5', '2011-02-19-356b619487-a3a5157286',
    '2011-03-20-2034e14341-7f2937223d', '2011-03-25-8138f7de40-3acdca4703',
    '2011-03-26-3acdca4703-c2fe893985', '2011-04-06-18d71a6f59-187eb235fe',
    '2011-04-07-77ed819430-efcb9a71cd', '2011-04-08-efcb9a71cd-6f3148db81',
    '2011-04-30-9c285fddbb-93f65cdeac', '2011-05-13-db0c957f02-8ba00176f1',
    '2011-05-17-453c954f8a-daecb2c0f4', '2011-05-21-f5a9e17f9c-964f44a280',
    '2011-05-24-b60f6774dc-1056c57fa9', '2011-10-30-c1a4a36c14-5921e73a37',
    '2011-10-31-2e5d5e5ac6-b5f15ef561', '2011-11-01-735efbdd04-e0f781f496',
    '2011-11-01-ceac9dc490-9b0d73af1d', '2011-11-01-d2881adcbc-4591498df7',
    '2011-11-02-c1d520d19d-9b86852d6e', '2011-11-02-de50e98a07-8d520d6296',
    '2011-11-04-9da01ac6b6-7334dfd7eb', '2011-11-15-236120d80e-fb37f3b20d',
    '2011-11-16-55acfdf7bd-3c7a573a2c', '2011-11-23-eca88d3064-db0888dfc1',
    '2011-12-04-b3ad0b7af7-1d6c98a136', '2011-12-10-74343ca506-52c36e60c4',
    '2011-12-17-db63456a8d-3dc9f0abe6', '2011-12-18-beda5efd41-622412d8e6',
    '2012-01-13-583292ab22-d74a258f24', '2012-01-16-f32760bd40-032d140fd6',
    '2012-02-18-0a91432828-032bbc3164', '2012-02-20-0cb26060af-eefefddc0e',
    '2012-02-25-38b549ea2f-1923ecfe25', '2012-03-02-730b54a374-1953161b8c',
    '2012-03-04-60dfd64bf2-34fe62619d', '2012-03-04-bda5ea7111-60dfd64bf2',
    '2012-03-19-53e3467ff2-9a460497da', '2007-07-08-bd2f947-ccc10c7',
    '2007-07-08-c766cb7-0cc95fb', '37171-37170', '37172-37171', '37172-37173',
    '37190-37191')

logging.basicConfig(
    level=logging.INFO,
    format=
    "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    datefmt="%H:%M:%S")


def init(args):
    if not os.path.isdir(OUT_DIR):
        os.mkdir(OUT_DIR)
    global timestamp
    if args.timestamp:
        timestamp = args.timestamp
    else:
        timestamp = datetime.today().strftime('%Y%m%d-%H:%M:%S')

    if not (args.case):
        docker_pull_ps = subprocess.run(
            ['docker', 'pull', '-a', 'prosyslab/manybugs'])
        docker_pull_ps.check_returncode()

    docker_list_process = subprocess.run(['docker', 'images'],
                                         capture_output=True,
                                         text=True)
    docker_list_process.check_returncode()
    entire_docker_list = docker_list_process.stdout.split('\n')

    tag_start_idx = entire_docker_list[0].find('TAG')
    tag_end_idx = entire_docker_list[0].find('IMAGE')

    for docker in entire_docker_list:
        repo = docker[0:tag_start_idx].strip()
        if repo != "prosyslab/manybugs":
            continue
        tag = docker[tag_start_idx:tag_end_idx].strip()
        project = tag.split('-')[0]
        case = tag[len(project) + 1:]
        if case in except_case_list:
            continue
        if project in bug_dict:
            bug_dict[project].append(case)
        else:
            bug_dict[project] = [case]


def build_one(project, case):
    if project in bug_dict and case in bug_dict[project]:
        logging.info(f'{project}-{case} is already installed. Skip')
    else:
        pull_process = subprocess.run(
            ['docker', 'pull', f'prosyslab/manybugs:{project}-{case}'])
        try:
            pull_process.check_returncode()
        except subprocess.CalledProcessError:
            logging.error(
                f'error occurred while pulling {project}-{case}. Skip')
            return False
        logging.info(f'{project}-{case} is successfully pulled')
    return True


localizer_options = {
    "lighttpd": ["-blacklist", "configparser.c", "-j", "1"],
    "gmp": [
        "-blacklist", "gen-jacobitab.c", "-blacklist", "gen-fib.c",
        "-blacklist", "gen-trialdivtab.c", "-blacklist", "gen-fac_ui.c",
        "-blacklist", "gen-psqr.c", "-blacklist", "gen-bases.c", "-blacklist",
        "dumbmp.c", "-gnu_source"
    ],
    "php": ["-gnu_source", "-j", "1"],
    "wireshark": [
        "-blacklist", "reassemble.c", "-blacklist", "packet-gtpv2.c",
        "-blacklist", "packet-dns.c", "-blacklist", "packet-nas_eps.c",
        "-blacklist", "lemon.c", "-gnu_source", "-j", "1"
    ]
}

php_blacklists = {
    "2011-01-06-e7a1d5004e-3571c955b5": ["-blacklist", "spl_iterators.c"],
    "2011-01-09-7c6310852e-478e5d1dd0":
    ["-blacklist", "zend_builtin_functions.c"],
    "2011-01-18-95388b7cda-b9b1fb1827": ["-blacklist", "document.c"],
    "2011-01-18-b5e12bd4da-163b3bcec9": ["-blacklist", "document.c"],
    "2011-01-23-bc049ccb62-a6c0a4e474": ["-blacklist", "php_date.c"],
    "2011-01-24-a6c0a4e474-1a8b87d2c5": ["-blacklist", "php_date.c"],
    "2011-01-29-147382033a-5bb0a44e06": ["-blacklist", "php_date.c"],
    "2011-01-30-5bb0a44e06-1e91069eb4": ["-blacklist", "php_date.c"],
    "2011-02-01-01745fa657-1f49902999": ["-blacklist", "userspace.c"],
    "2011-02-01-1f49902999-f2329f1f4b": ["-blacklist", "php_reflection.c"],
    "2011-02-01-fefe9fc5c7-0927309852": ["-blacklist", "phar.c"],
    "2011-02-04-793cfe1376-109b8e99e0": ["-blacklist", "url.c"],
    "2011-02-05-c50b3d7add-426f31e790": ["-blacklist", "url.c"],
    "2011-02-11-f912a2d087-b84967d3e2": ["-blacklist", "zend_execute.c"],
    "2011-02-14-86efc8e55e-d1d61ce612": ["-blacklist", "fileinfo.c"],
    "2011-02-16-eb0dd2b8ab-9bbc114b59": ["-blacklist", "userspace.c"],
    "2011-02-19-356b619487-a3a5157286": [
        "-blacklist", "basic_functions.c", "-blacklist", "streamsfuncs.c",
        "-blacklist", "plain_wrapper.c", "-blacklist", "xp_socket.c"
    ],
    "2011-02-21-2a6968e43a-ecb9d8019c": ["-blacklist", "json.c"],
    "2011-02-21-b21f62eb2d-2a6968e43a":
    ["-blacklist", "snprintf.c", "-blacklist", "spprintf.c"],
    "2011-02-27-e65d361fde-1d984a7ffd": ["-blacklist", "tokenizer.c"],
    "2011-03-11-d890ece3fc-6e74d95f34": ["-blacklist", "url.c"],
    "2011-03-19-5d0c948296-8deb11c0c3": ["-blacklist", "spl_directory.c"],
    "2011-03-20-2034e14341-7f2937223d":
    ["-blacklist", "file.c", "-blacklist", "streams.c"],
    "2011-03-22-0de2e61cab-991ba13174": ["-blacklist", "php_date.c"],
    "2011-03-23-63673a533f-2adf58cfcf": ["-blacklist", "php_date.c"],
    "2011-03-25-8138f7de40-3acdca4703": ["-blacklist", "phar_object.c"],
    "2011-03-26-3acdca4703-c2fe893985": [
        "-blacklist", "php_spl.c", "-blacklist", "spl_directory.c",
        "-blacklist", "spl_iterators.c"
    ],
    "2011-03-27-11efb7295e-f7b7b6aa9e": ["-blacklist", "php_spl.c"],
    "2011-03-27-2191af9546-b83e243c23": ["-blacklist", "spl_iterators.c"],
    "2011-04-02-70075bc84c-5a8c917c37": ["-blacklist", "string.c"],
    "2011-04-06-187eb235fe-2e25ec9eb7":
    ["-blacklist", "zend_object_handlers.c"],
    "2011-04-06-18d71a6f59-187eb235fe": ["-blacklist", "array.c"],
    "2011-04-07-77ed819430-efcb9a71cd": ["-blacklist", "zend_variables.c"],
    "2011-04-07-d3274b7f20-77ed819430": ["-blacklist", "spl_array.c"],
    "2011-04-08-efcb9a71cd-6f3148db81": [
        "-blacklist", "zend_builtin_functions.c", "-blacklist",
        "zend_exceptions.c", "-blacklist", "mysqlnd_bt.c"
    ],
    "2011-04-09-db01e840c2-09b990f499": ["-blacklist", "libxml.c"],
    "2011-04-12-465ffa7fa2-c4a8866abb": ["-blacklist", "string.c"],
    "2011-04-19-11941b3fd2-821d7169d9": ["-blacklist", "zend_closures.c"],
    "2011-04-27-53204a26d2-118695a4ea": ["-blacklist", "filter.c"],
    "2011-04-30-9c285fddbb-93f65cdeac": ["-blacklist", "streams.c"],
    "2011-05-13-db0c957f02-8ba00176f1": ["-blacklist", "zend_compile.c"],
    "2011-05-17-453c954f8a-daecb2c0f4": ["-blacklist", "nolocation"],
    "2011-05-21-f5a9e17f9c-964f44a280": ["-blacklist", "php_crypt_r.c"],
    "2011-05-24-b60f6774dc-1056c57fa9": ["-blacklist", "url_scanner_ex.c"],
    "2011-10-15-0a1cc5f01c-05c5c8958e": ["-blacklist", "zend_compile.c"],
    "2011-10-16-1f78177e2b-d4ae4e79db": ["-blacklist", "json.c"],
    "2011-10-30-c1a4a36c14-5921e73a37": ["-blacklist", "zend_compil.c"],
    "2011-10-31-2e5d5e5ac6-b5f15ef561": ["-blacklist", "zend_compile.c"],
    "2011-10-31-c4eb5f2387-2e5d5e5ac6": ["-blacklist", "zend_API.c"],
    "2011-11-01-735efbdd04-e0f781f496": [
        "-blacklist", "zend_closures.c", "-blacklist", "zend_gc.c",
        "-blacklist", "zend_object_handlers.c"
    ],
    "2011-11-01-ceac9dc490-9b0d73af1d": ["-blacklist", "zend_compile.c"],
    "2011-11-01-d2881adcbc-4591498df7": ["-blacklist", "zend_compile.c"],
    "2011-11-02-c1d520d19d-9b86852d6e": ["-blacklist", "spl_directory.c"],
    "2011-11-02-de50e98a07-8d520d6296": ["-blacklist", "zend_compile.c"],
    "2011-11-04-9da01ac6b6-7334dfd7eb": ["-blacklist", "zend_compile.c"],
    "2011-11-05-7888715e73-ff48763f4b":
    ["-blacklist", "zend_language_parser.c"],
    "2011-11-08-0ac9b9b0ae-cacf363957": ["-blacklist", "pdo_dbh.c"],
    "2011-11-08-6a42b41c3d-5063a77128": ["-blacklist", "tokenizer.c"],
    "2011-11-08-c3e56a152c-3598185a74":
    ["-blacklist", "zend_builtin_functions.c"],
    "2011-11-11-fcbfbea8d2-c1e510aea8": ["-blacklist", "spl_directory.c"],
    "2011-11-15-236120d80e-fb37f3b20d": ["-blacklist", "file.c"],
    "2011-11-15-2568672691-13ba2da5f6": ["-blacklist", "basic_functions.c"],
    "2011-11-16-55acfdf7bd-3c7a573a2c": ["-blacklist", "zend_compile.c"],
    "2011-11-19-51a4ae6576-bc810a443d": ["-blacklist", "zend_compile.c"],
    "2011-11-19-eeba0b5681-d3b20b4058": ["-blacklist", "mod_mm.c"],
    "2011-11-19-eeba0b5681-f330c8ab4e": ["-blacklist", "phar.c"],
    "2011-11-22-ecc6c335c5-b548293b99": ["-blacklist", "php_reflection.c"],
    "2011-11-23-eca88d3064-db0888dfc1": ["-blacklist", "zend_compile.c"],
    "2011-11-25-3b1ce022f1-c2ede9a00a": ["-blacklist", "parse_date.c"],
    "2011-11-26-7c2946f80e-dc6ecd21ee": ["-blacklist", "parse_date.c"],
    "2011-12-04-1e6a82a1cf-dfa08dc325": ["-blacklist", "logical_filters.c"],
    "2011-12-04-b3ad0b7af7-1d6c98a136": ["-blacklist", "zend_compile.c"],
    "2011-12-06-5087b0ee42-ac631dd580": [
        "-blacklist", "parse_date.c", "-blacklist", "tm2unixtime.c",
        "-blacklist", "php_date.c"
    ],
    "2011-12-10-74343ca506-52c36e60c4": ["-blacklist", "streams.c"],
    "2011-12-17-db63456a8d-3dc9f0abe6": ["-blacklist", "zend_compile.c"],
    "2011-12-18-beda5efd41-622412d8e6": ["-blacklist", "zend_execute.c"],
    "2012-01-01-7c3177e5ab-e2a2ed348f": ["-blacklist", "string.c"],
    "2012-01-01-80dd931d40-7c3177e5ab": ["-blacklist", "rfc1867.c"],
    "2012-01-13-583292ab22-d74a258f24": ["-blacklist", "zend_compile.c"],
    "2012-01-16-36df53421e-f32760bd40": ["-blacklist", "output.c"],
    "2012-01-16-f32760bd40-032d140fd6": [
        "-blacklist", "zend_compile.c", "-blacklist", "zend_constants.c",
        "-blacklist", "zend_execute_API.c"
    ],
    "2012-01-17-032d140fd6-877f97cde1":
    ["-blacklist", "zend_language_scanner.c"],
    "2012-01-17-e76c1cc03c-ebddf8a975": ["-blacklist", "php_reflection.c"],
    "2012-01-27-544e36dfff-acaf9c5227": ["-blacklist", "mod_user.c"],
    "2012-01-29-d8b312845c-dc27324dd9":
    ["-blacklist", "php_pdo_sqlite_int.h", "-blacklist", "sqlite_driver.c"],
    "2012-01-30-9de5b6dc7c-4dc8b1ad11": ["-blacklist", "string.c"],
    "2012-02-08-ff63c09e6f-6672171672": ["-blacklist", "php_variables.c"],
    "2012-02-12-3d898cfa3f-af92365239": ["-blacklist", "array.c"],
    "2012-02-18-0a91432828-032bbc3164": ["-blacklist", "phar_object.c"],
    "2012-02-20-0cb26060af-eefefddc0e":
    ["-blacklist", "zend_language_scanner.c"],
    "2012-02-25-38b549ea2f-1923ecfe25": ["-blacklist", "zend_API.c"],
    "2012-02-25-c1322d2505-cfa9c90b20": ["-blacklist", "zend_API.c"],
    "2012-03-02-730b54a374-1953161b8c":
    ["-blacklist", "zend_language_scanner.c"],
    "2012-03-04-60dfd64bf2-34fe62619d": ["-blacklist", "zend_compile.c"],
    "2012-03-04-bda5ea7111-60dfd64bf2": ["-blacklist", "zend_compile.c"],
    "2012-03-06-6237456cae-5e80c05deb": ["-blacklist", "fileinfo.c"],
    "2012-03-08-0169020e49-cdc512afb3": ["-blacklist", "streams.c"],
    "2012-03-08-d54e6ce832-23e65a9dcc": ["-blacklist", "spl_array.c"],
    "2012-03-10-23e65a9dcc-e6ec1fb166": ["-blacklist", "spl_array.c"],
    "2012-03-11-3954743813-d4f05fbffc": ["-blacklist", "zend_exceptions.c"],
    "2012-03-12-438a30f1e7-7337a901b7": ["-blacklist", "basic_functions.c"],
    "2012-03-12-7aefbf70a8-efc94f3115": ["-blacklist", "html.c"],
    "2012-03-19-53e3467ff2-9a460497da": ["-blacklist", "streams.c"],
    "2012-03-22-3efc9f2f78-2e19cccad7": ["-blacklist", "spl_directory.c"]
}


def run_one_localizer(args, project, case, engine):
    cmd = [f'{RUN_DOCKER_SCRIPT}', f'{project}-{case}', '-d']
    run_docker = subprocess.run(cmd)
    run_docker.check_returncode()
    docker_ps = subprocess.run(['docker', 'ps'],
                               capture_output=True,
                               text=True)
    docker_ps.check_returncode()
    dockers = docker_ps.stdout.split('\n')[1:]
    docker_id = None
    for d in dockers:
        container_id, image = d.split()[:2]
        if image == f'prosyslab/manybugs:{project}-{case}':
            docker_id = container_id
            break
    if not docker_id:
        logging.error(f'Cannot find container_id of {project}:{case}')
        return
    # TODO: -skip_compile
    options = localizer_options[
        project] if project in localizer_options else []
    if project == "php":
        options.extend(php_blacklists[case])
        print(os.getcwd())
        script_copy_cmd = [
            'docker', 'cp', './bin/php_script.sh', f'{docker_id}:/experiment'
        ]
        script_copy = subprocess.run(script_copy_cmd)
        try:
            script_copy.check_returncode()
        except subprocess.CalledProcessError:
            logging.error(f'{project}:{case} script copy failure')
        script_run_cmd = [
            'docker', 'exec', f'{docker_id}', '/experiment/php_script.sh'
        ]
        script_run = subprocess.run(script_run_cmd)
        try:
            script_run.check_returncode()
        except subprocess.CalledProcessError:
            logging.error(f'{project}:{case} script run failure')
    localizer_cmd = [
        'docker', 'exec', '-it', f'{docker_id}',
        '/bugfixer/localizer/main.exe', '-engine', engine
    ] + options + (['-gcov'] if args.gcov else []) + ['/experiment']
    localizer = subprocess.run(localizer_cmd)
    try:
        localizer.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'{project}:{case} localizer execution failure')
        return
    out_dir_case = os.path.join(OUT_DIR, project, f'{project}:{case}')
    os.makedirs(out_dir_case, exist_ok=True)
    out_dir_timestamp = os.path.join(out_dir_case, timestamp + '-' + engine)
    cp_cmd = [
        'docker', 'cp', f'{docker_id}:/experiment/localizer-out',
        out_dir_timestamp
    ]
    run_cp = subprocess.run(cp_cmd)
    try:
        run_cp.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(
            f'{project}:{case} localizer executed successfully, but docker cp returns non-zero code'
        )
    stop_cmd = ['docker', 'stop', f'{docker_id}']
    stop = subprocess.run(stop_cmd)
    try:
        stop.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'Cannot stop docker container of {project}:{case}')
    rm_cmd = ['docker', 'rm', f'{docker_id}']
    rm = subprocess.run(rm_cmd)
    try:
        rm.check_returncode()
    except subprocess.CalledProcessError:
        logging.error(f'Cannot remove docker continer of {project}:{case}')


def build_and_run(args):
    project, case, engine = args.project, args.case, args.engine
    if project:
        if case:
            if build_one(project, case):
                if engine:
                    run_one_localizer(args, project, case, engine)
                else:
                    run_one_localizer(args, project, case, 'all')
        else:
            for case in bug_dict[project]:
                if build_one(project, case):
                    if engine:
                        run_one_localizer(args, project, case, engine)
                    else:
                        run_one_localizer(args, project, case, 'all')
    else:
        for project in bug_dict:
            for case in bug_dict[project]:
                if build_one(project, case):
                    if engine:
                        run_one_localizer(args, project, case, engine)
                    else:
                        run_one_localizer(args, project, case, 'all')


def main():
    parser = argparse.ArgumentParser(description='Build bugs using BugZoo.')
    parser.add_argument('-t', '--timestamp', type=str)
    parser.add_argument('-p', '--project', type=str)
    parser.add_argument('-c', '--case', type=str)
    parser.add_argument('-e', '--engine', type=str)
    parser.add_argument('-g', '--gcov', action="store_true", default=False)
    args = parser.parse_args()
    init(args)
    build_and_run(args)


if __name__ == '__main__':
    main()
