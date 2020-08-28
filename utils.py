from yclient import ChainClient
import pymongo
import os
from pathlib import Path
import time
from tqdm import tqdm


def get_archive_node():
    return os.getenv('ARCHIVENODE_API')


def get_project_root():
    return str(Path(__file__).parent.parent)


def get_mongo():
    return os.getenv('MONGO')


def get_archive_client():
    return ChainClient(get_archive_node())


def get_mongo_client():
    return pymongo.MongoClient(get_mongo())


def get_yvault_db():
    return get_mongo_client()['yvault']


def get_roi_collection():
    return get_yvault_db()['roi2']


def get_info_collection():
    return get_yvault_db()['info']


def get_prices_collection():
    return get_yvault_db()['prices']


def get_vault_data():
    db = get_info_collection()
    cursor = db.find({}, {'_id': 0})
    for i in cursor:
        return i


def pull_roi():
    coll = []
    vault = []
    for d in get_roi_collection().find({}, {'_id': 0}).limit(14).sort([('ts', -1), ('vault', -1)]):
        if d['vault'] not in vault:
            coll.append(d)
            vault.append(d['vault'])

    return coll


def push_roi():
    vault_data = get_vault_data()

    cc = get_archive_client()

    blocks = {'Historic average daily': cc.get_block_at_time(60 * 60 * 24),
              'Historic average weekly': cc.get_block_at_time(60 * 60 * 24 * 7)}
    i = 0
    for v in vault_data:
        if v != 'yearn Curve.fi yDAI/yUSDC/yUSDT/yTUSD':
            cc.setup(vault_data[v]['address'])
            roi = {'vault': v}
            a = vault_data[v]['address']
            roi['address'] = a

            for b in blocks:
                mbar = tqdm(desc='Processing blocks for ' + v)
                if blocks[b] > vault_data[v]['first_block']:
                    roi[b] = cc.get_roi_set(blocks[b])
                    mbar.update()
            sb = vault_data[v]['first_strategy_block']
            roi['Historic average since strategy change'] = cc.get_roi_set(sb)
            fb = vault_data[v]['first_block']
            roi['Historic average since inception'] = cc.get_roi_set(fb)
            roi['ts'] = int(time.time())
            try:
                get_roi_collection().insert_one(roi)
            except:
                None

