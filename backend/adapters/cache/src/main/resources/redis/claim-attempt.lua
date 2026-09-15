
local raw = redis.call('GET', KEYS[1])
if not raw then
    return {'missing'}
end
local record = cjson.decode(raw)
record['attempts'] = record['attempts'] + 1
if record['attempts'] >= tonumber(ARGV[1]) then
    local pointer_key = '{pointer_prefix}' .. record['challengeType']
        .. '{pointer_middle}' .. record['uniquenessKey'] .. '{pointer_suffix}'
    redis.call('DEL', KEYS[1])
    if redis.call('GET', pointer_key) == record['id'] then
        redis.call('DEL', pointer_key)
    end
    return {'exhausted'}
end
local encoded = cjson.encode(record)
redis.call('SET', KEYS[1], encoded, 'KEEPTTL')
return {'claimed', encoded}
