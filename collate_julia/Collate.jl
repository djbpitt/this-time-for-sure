#=
Collate:
- Julia version: 1.0.3
- Author: rhdekker
- Date: 2018-12-28
=#


using DataStructures

# create witness data
# TODO: Make ordered dict!

witnessData = Dict( "wit1" => ["a", "b", "c", "d", "e"],
                    "wit2" => ["a", "e", "c","d"],
                    "wit3" => ["a", "d", "b"])

println(typeof(witnessData))
println(witnessData)

csTable = DefaultDict{Tuple, Vector{Tuple{String, Int64, Int64}}}(Vector)

for (key, value) in witnessData
    println(key)
#    println(value[1:end])
    for idx in 1:length(value)
        # println("idx1 ", idx)
        for idx2 in idx+1:length(value)
            # println("idx2 ", idx2 )
            push!(csTable[(value[idx], value[idx2])], (key, idx, idx2))
        end
    end
end


    ###
    # Sort table into common sequence list (csList)
    ###
    #   order by 1) number of witnesses (numerical high to low) and 2) sequence (alphabetic low to high)
    # This works but seems more complicated than needed.
    csList = sort(collect(keys(csTable)), by = key -> (-length(csTable[key]), key))


# for item in csList
#     println(item, " ==> ", csTable[item])
# end


mutable struct Node
    normalized::String
end

struct Token
    witnessId::String
    normalized::String
    position::Int32
end

###
# Build topological ordered list
###
toList = Vector{Node}()
append!(toList, [Node("#start"), Node("#end")])

for normalized_skipgram in csList
    skipgrams = csTable[normalized_skipgram]
    for skipgram in skipgrams
        # each skipgram has two tokens
        # For each token we need the witness id (in the skipgram)
        # the normalized form (in the normalized_skipgram as a tuple)
        # each token has a location within the witness
        # both tokens are from the same witness
        # TODO: in the future the non-normalized representation would also need to be fetched from the witness data
        witnessIdentifier = skipgram[1]
        for token_number in 1:2
            normalized = normalized_skipgram[token_number]
            offset = skipgram[token_number+1]
#            println("Token: ", witnessIdentifier, ", ", normalized, ", ", offset)
            token = Token(witnessIdentifier, normalized, offset)
            println(token)
        end
    end
    # TODO: for now to control the flow of the output
    break
end
