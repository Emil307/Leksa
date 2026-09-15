
local pointer = redis.call('GET', KEYS[2])
if pointer and pointer ~= ARGV[2] then
    local previous = redis.call('GET', '{record_key_prefix}' .. pointer)
    if previous then
        local created_at = string.match(previous, '"createdAt":%s*"([^"]*)"')
        if created_at and created_at > ARGV[4] then
            return 0
        end
        redis.call('DEL', '{record_key_prefix}' .. pointer)
    end
end
redis.call('SET', KEYS[1], ARGV[1], 'EX', ARGV[3])
redis.call('SET', KEYS[2], ARGV[2], 'EX', ARGV[3])
return 1
