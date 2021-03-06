# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.
import itertools
class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return a String representing its
    # answer to the question: "1", "2", "3", "4", "5", or "6". These Strings
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName().
    #
    # In addition to returning your answer at the end of the method, your Agent
    # may also call problem.checkAnswer(String givenAnswer). The parameter
    # passed to checkAnswer should be your Agent's current guess for the
    # problem; checkAnswer will return the correct answer to the problem. This
    # allows your Agent to check its answer. Note, however, that after your
    # agent has called checkAnswer, it will#not* be able to change its answer.
    # checkAnswer is used to allow your Agent to learn from its incorrect
    # answers; however, your Agent cannot change the answer to a question it
    # has already answered.
    #
    # If your Agent calls checkAnswer during execution of Solve, the answer it
    # returns will be ignored; otherwise, the answer returned at the end of
    # Solve will be taken as your Agent's answer to this problem.
    #
    # @param problem the RavensProblem your agent should solve
    # @return your Agent's answer to this problem
    def Solve(self,problem):
        print "Working on problem", problem.getName()
        
        #Potential answers will go in a list
        answer = []
        #Get Figure objects
        A = problem.getFigures().get("A")
        B = problem.getFigures().get("B")
        C = problem.getFigures().get("C")
        one = problem.getFigures().get("1")
        two = problem.getFigures().get("2")
        three = problem.getFigures().get("3")
        four = problem.getFigures().get("4")
        five = problem.getFigures().get("5")
        six = problem.getFigures().get("6")

        #generate transformation relationships between frames. Returns dictionary of {objectName: transformations}
        AtoB = self.getRelationships(A,B,{},problem)
        Cto1 = self.getRelationships(C,one,AtoB,problem)
        Cto2 = self.getRelationships(C,two,AtoB,problem)
        Cto3 = self.getRelationships(C,three,AtoB,problem)
        Cto4 = self.getRelationships(C,four,AtoB,problem)
        Cto5 = self.getRelationships(C,five,AtoB,problem)
        Cto6 = self.getRelationships(C,six,AtoB,problem)

        possible = {"1":Cto1, "2":Cto2, "3":Cto3, "4":Cto4, "5":Cto5, "6":Cto6}

        #Choose answers C-># with similar transformations as A->B
        scores = {} #naive 'delta' score
        for name,rels in possible.iteritems():
            scores[name] = 0
            for AtoBval,relsval in zip(AtoB.values(),rels.values()):
                scores[name] += len(set(AtoBval).intersection(relsval))
        
        for name,score in scores.iteritems():
                if score == max(scores.itervalues()):
                    answer.append(name)

        print "Answers after transformations:", answer
        #if there is more than one possible answer, compare relative positions of objects in B with solutions
        if len(answer) > 1:
            #generate positional relationships in frames B and 1-6
            B_pos = self.getPositions(B)
            one_pos = self.getPositions(one)
            two_pos = self.getPositions(two)
            three_pos = self.getPositions(three)
            four_pos = self.getPositions(four)
            five_pos = self.getPositions(five)
            six_pos = self.getPositions(six)

            possible = {"1":one_pos, "2":two_pos, "3":three_pos, "4":four_pos, "5":five_pos, "6":six_pos}
            #eliminate answers not in answer
            for k in possible.keys(): 
                if k not in answer:
                    del possible[k]
            #eliminate answers with different positions than B
            
            scores = {} #naive 'delta' score
            for name,positions in possible.iteritems():
                scores[name] = len(set(map(tuple,B_pos)).intersection(map(tuple,positions)))

            for name,score in scores.iteritems():
                if score < max(scores.itervalues()):
                    answer.remove(name)

        print "Answers after positions:", answer
        #if there is still more than one possible answer, compare frames B with potential answers for similarity
                    #e.g. are all shapes same size? same fill or different? etc.
        if len(answer) > 1:
            B_fr = self.FrameSimilarity(B)
            one_fr = self.FrameSimilarity(one)
            two_fr = self.FrameSimilarity(two)
            three_fr = self.FrameSimilarity(three)
            four_fr = self.FrameSimilarity(four)
            five_fr = self.FrameSimilarity(five)
            six_fr = self.FrameSimilarity(six)

            possible = {"1":one_fr, "2":two_fr, "3":three_fr, "4":four_fr, "5":five_fr, "6":six_fr}
            #eliminate answers not in answer
            for k in possible.keys(): 
                if k not in answer:
                    del possible[k]
            #pick frame most similar to B
            scores = {}
            for name,frames in possible.iteritems():
                scores[name] = len(set(B_fr).intersection(frames))
            for name,score in scores.iteritems():
                if score < max(scores.itervalues()):
                    answer.remove(name)
        print "Answers after frame comparisons:", answer
        print ""
        return min(answer) if len(answer) > 0 else "1" #pick one randomly if multiple answers left. If there are no answers left choose 1 (shouldn't happen)





    def getRelationships(self,A,B,matchWith,problem):
        #generates a dictionary of lists of relations between each object A->B
        #examines each possible mapping of objects from A->B and picks best mapping based on weight
        A_Objs = A.getObjects()
        B_Objs = B.getObjects()
        
        A_names = [A_Obj.getName() for A_Obj in A_Objs]
        B_names = [B_Obj.getName() for B_Obj in B_Objs]
        while len(A_names) != len(B_names):
            if len(A_names) > len(B_names):
                B_names.append(None)
            if len(B_names) > len(A_names):
                A_names.append(None)
        B_permutations = list(itertools.permutations(B_names))

        bestweight = 0
        bestrels = {}
        for B_names in B_permutations:
            weight = 0
            rels = {}
            
            for A_name,B_name in zip(A_names,B_names):
                
                for obj in A_Objs:
                    if obj.getName() == A_name:
                        A_Obj = obj
                for obj in B_Objs:
                    if obj.getName() == B_name:
                        B_Obj = obj
                if not A_name:
                    #obj was added to b
                    rels[B_name] = []
                    rels[B_name].append("added")
                elif not B_name:
                    #obj was deleted from a
                    rels[A_name] = []
                    rels[A_name].append("deleted")
                else:
                    rels[B_name] = []
                    A_atts = {}
                    B_atts = {}
                    for A_att,B_att in zip(A_Obj.getAttributes(),B_Obj.getAttributes()):
                        A_atts[A_att.getName()] = A_att.getValue()
                        B_atts[B_att.getName()] = B_att.getValue()

                    #now for some attribute rules:
                    #shape
                    try:
                        if A_atts["shape"] == B_atts["shape"]:
                            rels[B_name].append("shapeSame")
                            weight += 5
                        else:
                            rels[B_name].append("shapeDiff")
                    except KeyError:
                        pass

                    #size
                    try:
                        if A_atts["size"] == B_atts["size"]:
                            rels[B_name].append("sizeSame")
                            weight += 5
                        else:
                            rels[B_name].append("sizeDiff")
                            weight += 2
                    except KeyError:
                        pass

                    #fill
                    try:
                        A_atts["fill"]
                    except KeyError:
                        A_atts["fill"] = "no"

                    try:
                        B_atts["fill"]
                    except KeyError:
                        B_atts["fill"] = "no"
                    
                    if A_atts["fill"] == B_atts["fill"]:
                        rels[B_name].append("fillSame")
                        weight += 5
                    else:
                        rels[B_name].append("fill:" + A_atts["fill"] + B_atts["fill"])
                        weight += 2
                    
                    #angle
                    try:
                        A_atts["angle"]
                    except KeyError:
                        A_atts["angle"] = 0
                    try:
                        B_atts["angle"]
                    except KeyError:
                        B_atts["angle"] = 0
                     
                    if A_atts["shape"] == "circle" and B_atts["shape"] == "circle": #ignore angle changes for circle
                        if matchWith:
                            for obj in matchWith.iterkeys():
                                if 'angleDiff' in matchWith[obj]:
                                    rels[B_name].append('angleDiff')
                                    rels[B_name].append([n for n in matchWith[obj] if type(n) == type(1)][0]) #copy angle value
                                    break
                                if 'angleSame' in matchWith[obj]:
                                    rels[B_name].append('angleSame')
                                    break
                        elif A_atts["angle"] == B_atts["angle"]:
                            rels[B_name].append("angleSame")
                            weight += 4
                        
                    elif A_atts["angle"] == B_atts["angle"]:
                        rels[B_name].append("angleSame")
                        weight += 4
                    else:
                        rels[B_name].append("angleDiff")
                        rels[B_name].append(abs(int(A_atts["angle"]) - int(B_atts["angle"])))
                        weight +=3

                    #vertical-flip
                    try:
                        A_atts["vertical-flip"]
                    except KeyError:
                        A_atts["vertical-flip"] = "no"
                    try:
                        B_atts["vertical-flip"]
                    except KeyError:
                        B_atts["vertical-flip"] = "no"

                    if A_atts["vertical-flip"] == B_atts["vertical-flip"]:
                        rels[B_name].append("vertflipSame")
                        
                    else:
                        rels[B_name].append("vertflipDiff")

            if rels == matchWith:
                weight += 100
            if weight > bestweight:
                bestrels = rels
                bestweight = weight
           
        return bestrels

    def getPositions(self,A):
        #get relationships between objects in one frame
        A_Objs = A.getObjects()
        A_names = [A_Obj.getName() for A_Obj in A_Objs]
        pos = []
        for A_Obj in A_Objs:
            A_atts = A_Obj.getAttributes()
            objpos = []
            
            for att in A_atts:
            
                try:
                    if att.getName() == "inside":
                        objpos.append("inside")
                except KeyError:
                    pass

                try:
                    if att.getName() == "above":
                        objpos.append("above")
                except KeyError:
                    pass

                try:
                    if att.getName() == "left-of":
                        objpos.append("left-of")
                except KeyError:
                    pass
                try:
                    if att.getName() == "overlaps":
                        objpos.append("overlaps")
                except KeyError:
                    pass
            pos.append(objpos)
      
        return pos

    def FrameSimilarity(self,A):
        #determine if all shapes in a frame share properties or not
        A_Objs = A.getObjects()
        frameDesc = []
        shape = []
        size = []
        fill = []
        rotation = []
        for A_Obj in A_Objs:
            A_atts = A_Obj.getAttributes()
            for att in A_atts:
                try:
                    if att.getName() == "shape":
                        shape.append(att.getValue())
                except KeyError:
                    pass
                try:
                    if att.getName() == "size":
                        size.append(att.getValue())
                except KeyError:
                    pass
                try:
                    if att.getName() == "fill":
                        fill.append(att.getValue())
                except KeyError:
                    pass
                try:
                    if att.getName() == "rotation":
                        rotation.append(att.getValue())
                except KeyError:
                    pass
        if len(set(shape)) <= 1:
            frameDesc.append("sameShape")
        else:
            frameDesc.append("diffShape")
        if len(set(size)) <= 1:
            frameDesc.append("sameSize")
        else:
            frameDesc.append("diffSize")
        if len(set(fill)) <= 1:
            frameDesc.append("sameFill")
        else:
            frameDesc.append("diffFill")
        if len(set(rotation)) <= 1:
            frameDesc.append("sameRotation")
        else:
            frameDesc.append("diffRotation")
        frameDesc.append(len(A_Objs)) #number of shapes
        return frameDesc
            
