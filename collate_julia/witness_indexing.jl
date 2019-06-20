#=
witness_indexing:
- Julia version: 
- Author: rhdekker
- Date: 2019-06-10
=#


# create token array
# this is hardcoded
function create_token_array()
    token_array = []
    append!(token_array, witnessData["wit1"])
    push!(token_array, "#")
    append!(token_array, witnessData["wit2"])
    push!(token_array, "#")
    append!(token_array, witnessData["wit3"])
    return token_array
end

# custom comparator to make suffix array based on tokens work
function less_than(i::Int64, j::Int64)
    if (token_array[i] < token_array[j])
        return true
    else
        return false
    end
end

function create_suffix_array()
    # create suffix array
    # the suffix array has the same length as the token array
    # for now we fill it with integers counting upwards
    suffix_array = collect(1:length(token_array))
#    println(suffix_array)

    # for a in suffix_array
    #     println(a)
    # end

    sort!(suffix_array, lt=less_than)
    return suffix_array
end


# create witness data
# TODO: Make ordered dict!

witnessData = Dict( "wit1" => ["a", "b", "c", "d", "e"],
                    "wit2" => ["a", "e", "c","d"],
                    "wit3" => ["a", "d", "b"])

println(typeof(witnessData))
println(witnessData)

token_array = create_token_array()
println(token_array)

suffix_array = create_suffix_array()
println(suffix_array)

# show the suffix array
for token_pointer in suffix_array
    sub_token_array = token_array[token_pointer:end]
    a = findfirst(x -> x == "#", sub_token_array)
    if a != nothing
        sub_token_array = sub_token_array[1:a]
    end
    println(sub_token_array)
end
