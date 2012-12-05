import json

with open('random.txt', 'r') as f:
    count = 1
    tdata = {'real':{'none':0, 'bad':0, 'good':0, 'neutral':0}, 'fake':{'none':0, 'bad':0, 'good':0, 'neutral':0}}
    rvalue = 0
    fvalue = 0
    for line in f.readlines():
        data = json.loads(line)
        print str(count) + ' & ' + str(data['real']['none']) + ' & ' + str(data['real']['good']) + ' & ' + str(data['real']['neutral']) + ' & ' + str(data['real']['bad']) + ' & ' + str(data['fake']['none']) + ' & ' + str(data['fake']['good']) + ' & ' + str(data['fake']['neutral']) + ' & ' + str(data['fake']['bad']) + ' \\\\'
        for k1 in data:
            for k2 in data[k1]:
                tdata[k1][k2] += data[k1][k2]
                if k2 == 'none':
                    v = -0.25
                elif k2 == 'good':
                    v = 2
                elif k2 == 'neutral':
                    v = 0
                elif k2 == 'bad':
                    v = -2
                if k1 == 'real':
                    rvalue += data[k1][k2] * v
                else:
                    fvalue += data[k1][k2] * v
        count += 1
    print 'Total & ' + str(tdata['real']['none']) + ' & ' + str(tdata['real']['good']) + ' & ' + str(tdata['real']['neutral']) + ' & ' + str(tdata['real']['bad']) + ' & ' + str(tdata['fake']['none']) + ' & ' + str(tdata['fake']['good']) + ' & ' + str(tdata['fake']['neutral']) + ' & ' + str(tdata['fake']['bad']) + ' \\\\'
    print rvalue, fvalue
