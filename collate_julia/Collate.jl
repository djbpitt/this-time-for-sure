#=
Collate:
- Julia version: 1.0.3
- Author: rhdekker
- Date: 2018-12-28
=#


using DataStructures

mutable struct Node
    normalized::String
end

struct Token
    witnessId::String
    normalized::String
    position::Int32
end



function find_lower_and_higher_bound_topological_list(token)
    println("Called!")
    # we are going over the topological list
    # from left to right
    # we filter out all the nodes that are not part of the witness of the token
    # in that case we move to the right
    # of course we can also skip the start and the end nodes
    # so initialy we set the lower and the upper bound to the start and end nodes.
    # so that is one for lower
    # and 2 for upper (length of topological list)
    # then we loop from lower +1 to upper -1 to see whether we can find a position for the token to place in.
    lower = 1
    upper = length(toList)
    for position in lower+1:upper-1
        println(position)
        #TODO: zoek
        end
    return lower, upper
end

function insert_token_in_topological_list(token, toList)
        lower, upper = find_lower_and_higher_bound_topological_list(token)
        # there are multiple possible situations
        # lower and upper differ by one a token needs to be inserted on the place of the upper
        if upper - lower == 1
            # convert token to node
            # TODO: Question is there an explicit way to implement conversation in Julia?
            node = Node(token.normalized)
            # TODO: I should not append at the end, but at the place of the upper bound
            # Maybe not use an array but an unrolled linked list?
            push!(toList, node)
        else
            println("NOT IMPLEMENTED YET!")
        end
end

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
            insert_token_in_topological_list(token, toList)
        end
    end
    # TODO: for now to control the flow of the output
    break
end

println(toList)

