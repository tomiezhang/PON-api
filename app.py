from flask import Flask
from flask import jsonify
import json
from PIL import Image
import requests
import os
import random
'''
#部署在自己服务器上的metadta-api服务器
#用于产生对应组合生成的NFT的元数据，组合后发送到合约地址
#同时合成的图片部署到IPFS地址上
'''
app = Flask(__name__)
#定义
BACKGROUND=list(range(1,27))
EAR=list(range(1,10))
EYE=list(range(1,10))
FACE=list(range(1,10))
MOUTH=list(range(1,10))
NOSE=list(range(1,10))
TOTAL= 666

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'
#API入口, /api/1
@app.route('/api/opera/<token_id>')
def opera(token_id):
    token_id = int(token_id)
    if token_id<TOTAL:
        # 查找output里是否生成过，生成过就不再生成直接返回元数据
        if os.path.exists("static/output/" + str(token_id) + ".json"):
            with open("static/output/" + str(token_id) + ".json", 'r') as load_f:
                load_dict = json.load(load_f)
                return jsonify(load_dict)
        else:
            #没有生成过
            background = BACKGROUND[token_id % len(BACKGROUND)]
            ear = EAR[token_id % len(EAR)]
            eye = EYE[token_id % len(EYE)]
            face = FACE[token_id % len(FACE)]
            mouth = MOUTH[token_id % len(MOUTH)]
            nose = NOSE[token_id % len(NOSE)]
            print("{}-{}-{}-{}-{}-{}".format(background, ear, eye, face, mouth, nose))
            image_url = _compose_image(['static/background/{}.jpg'.format(background), 'static/ear/{}.png'.format(ear),
                                        'static/face/{}.png'.format(face), 'static/mouth/{}.png'.format(mouth),
                                        'static/nose/{}.png'.format(nose), 'static/eye/{}.png'.format(eye)], token_id)
            attributes = []
            _add_attribute(attributes, 'background', BACKGROUND, token_id)
            _add_attribute(attributes, 'ear', EAR, token_id)
            _add_attribute(attributes, 'eye', EYE, token_id)
            _add_attribute(attributes, 'face', FACE, token_id)
            _add_attribute(attributes, 'mouth', MOUTH, token_id)
            _add_attribute(attributes, 'nose', NOSE, token_id)
            # 级别游戏可用_add_attribute(attributes, 'level', INT_ATTRIBUTES, token_id)
            # 耐力游戏可用_add_attribute(attributes, 'stamina', FLOAT_ATTRIBUTES, token_id)
            # 性格游戏可用_add_attribute(attributes, 'personality', STR_ATTRIBUTES, token_id)
            # 水上力量游戏可用_add_attribute(attributes, 'aqua_power', BOOST_ATTRIBUTES, token_id, display_type="boost_number")
            # 耐力增长游戏可用_add_attribute(attributes, 'stamina_increase', PERCENT_BOOST_ATTRIBUTES, token_id, display_type="boost_percentage")
            # 代数游戏可用_add_attribute(attributes, 'generation', NUMBER_ATTRIBUTES, token_id, display_type="number")
            if image_url != 1:
                #如果上传IPFS没有问题
                jsons = {
                    'name': "CryptoOpera %s" % token_id,
                    'description': "Crpto feelings from the far east.",
                    'image': image_url,
                    # 'external_url': 'https://example.com/?token_id=%s' % token_id,
                    'attributes': attributes
                }
                # 写入本地服务器
                with open("static/output/" + str(token_id) + ".json", "w") as f:
                    json.dump(jsons, f)
                return jsonify(jsons)
            else:
                return jsonify({
                    'stats': "wow!404"
                })
    else:
        return jsonify({
            'stats': "wow!404"
        })
#动态合成图片
def _compose_image(image_files, token_id):
    composite = None
    for image_file in image_files:
        foreground = Image.open(image_file).convert("RGBA")
        if composite:
            composite = Image.alpha_composite(composite, foreground)
        else:
            composite = foreground
    output_path = "static/output/%s.png" % token_id
    composite.save(output_path)
    #上传到IPFS
    IPFSadd = _sortInIPFS(output_path)
    if IPFSadd != 1:
        print("IPFS地址：ipfs://"+IPFSadd["Hash"])
        return "ipfs://"+IPFSadd["Hash"]
    else:
        print("IPFS上传失败！")
        return 1

#存储到IPFS上
def _sortInIPFS(path):
    print("path:"+path)
    files = {
        'file': open(path, mode='rb')
    }
    response = requests.post("https://ipfs.infura.io:5001/api/v0/add",files=files,auth=("20dw9iCz9m3lnfxfliWrxQ5F5Xc", "b66819c2d0518decd526a85eb5e5a7a0"))
    if response.status_code == 200 :
        return json.loads(response.text)
    else:
        return 1

#添加元数据属性
def _add_attribute(existing, attribute_name, options, token_id, display_type=None):
    trait = {
        'trait_type': attribute_name,
        'value': options[token_id % len(options)]
    }
    if display_type:
        trait['display_type'] = display_type
    existing.append(trait)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
