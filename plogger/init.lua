local plogger = {}

local function state_file(file)
    return vim.fn.fnamemodify(file, ":h") .. "/state.txt"
end

local function last_checksum(state_path)
    local f = io.open(state_path, "r")
    if not f then return nil end
    local last
    for line in f:lines() do last = line end
    f:close()
    return last and last:match("^(%w+)")
end

local function append(state_path, checksum)
    local f = io.open(state_path, "a")
    f:write(string.format("%s %d\n", checksum, os.time()))
    f:close()
end

local function on_save(file)
    if not file:match("%.plg$") then return end
    local handle = io.popen("md5sum " .. vim.fn.shellescape(file))
    local checksum = handle:read("*a"):match("^(%w+)")
    handle:close()

    local state_path = state_file(file)
    if last_checksum(state_path) ~= checksum then
        append(state_path, checksum)
    end
end

function plogger.setup()
    vim.api.nvim_create_autocmd("BufWritePost", {
        pattern = "*.plg",
        callback = function(args)
            on_save(args.file)
        end,
    })
end

return plogger
