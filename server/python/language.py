import string

#Constants
DIGITS="0123456789"
LETTERS=string.ascii_letters
LETTERS_DIGITS=LETTERS+DIGITS

#Error classes
class Error:
    def __init__(self,start,end,error_name,details):
        self.start=start
        self.end=end
        self.error_name=error_name
        self.details=details

    def show_error(self):
        error=f'{self.error_name}:{self.details}\n'
        error+=f'File{self.start.filename},line{self.start.line+1}'
        return error 

class IllegalCharacterError(Error):
    def __init__(self,start,end,details):
        super().__init__(start,end,"Illegal Character", details)

class ExpectedCharError(Error):
    def __init__(self, start, end,details):
        super().__init__(start, end, "Expected Character", details)

class InvalidSyntaxError(Error):
    def __init__(self, start, end,details=""):
        super().__init__(start, end,"Invalid Syntax", details)

class RunTimeError(Error):
    def __init__(self, start, end,details,context):
        super().__init__(start, end,"RunTimeError",details)
        self.context=context
    
    def show_error(self):
        error=self.generate_traceback()
        error+=f'{self.error_name}:{self.details}\n'
        return error

    def generate_traceback(self):
        error=""
        pos=self.start
        ctx=self.context

        while ctx:
            error+=f' File{pos.filename},line{str(pos.line+1)},in{ctx.display_name}\n'+error
            pos=ctx.parent_pos
            ctx=ctx.parent
        
        return 'Traceback (most recent call last):\n'+error

#Position Class
class Position:
    def __init__(self,index,line,col,filename,filetext):
        self.index=index
        self.line=line
        self.col=col
        self.filename=filename
        self.filetext=filetext

    def advance(self,current_char=None):
        self.index+=1
        self.col+=1
        if current_char=="\n":
            self.line+=1
            self.col=0
        return self

    def copy(self):
        return Position(self.index,self.line,self.col,self.filename,self.filetext)

#Tokens and Keywords
T_INT="INT"
T_FLOAT="FLOAT"
T_STRING="STRING"
T_IDENTIFIER="IDENTIFIER"
T_KEYWORD="KEYWORD"
T_EQUAL="EQUAL"
T_PLUS="PLUS"
T_MINUS="MINUS"
T_MULTIPLY="MULTIPLY"
T_DIVIDE="DIVIDE"
T_FLOORDIVIDE="FLOORDIVIDE"
T_MODULO="MODULO"
T_POWER="POWER"
T_LPAREN="LPAREN"
T_RPAREN="RPAREN"
T_LPAREN2="LPAREN2"
T_RPAREN2="RPAREN2"
T_LPAREN3="LPAREN3"
T_RPAREN3="RPAREN3"
T_NEWLINE="NEWLINE"
T_COLON="T_COLON"
T_EE="EE"
T_NE="NE"
T_LT="LT"
T_LTE="LTE"
T_GT="GT"
T_GTE="GTE"
T_COMMA="COMMA"
T_INDEX="INDEX"
T_EOF="EOF"

KEYWORD=["take","and","or","not","whether","further","ifnot","StartCycle","to","leap","AsLongAs","Method"]

#Token Class
class Token:
    def __init__(self,type_,value=None,start=None,end=None):
        self.type=type_
        self.value=value
        
        if start:
            self.start=start.copy()
            self.end=start.copy()
            self.end.advance()

        if end:
            self.end=end.copy()

    def matches(self,type_,value):
        return self.type==type_ and self.value==value

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

#Lexer Class
class Lexer:
    def __init__(self,filename,text):
        self.filename=filename
        self.text=text
        self.pos=Position(-1,0,-1,filename,text)
        self.current_char=None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        if self.pos.index<len(self.text):
            self.current_char=self.text[self.pos.index]
        else:
            self.current_char=None

    def make_number(self):
        num=""
        dot_count=0
        start=self.pos.copy()

        while self.current_char !=None and self.current_char in DIGITS+".":
            if self.current_char==".":
                if dot_count==1:
                    break
                dot_count+=1
                num+="."
            else:
                num+=self.current_char
            self.advance()

        if dot_count==0:
            return Token(T_INT,int(num),start,self.pos)
        else:
            return Token(T_FLOAT,float(num),start,self.pos)

    def make_string(self):
        string=""
        start=self.pos.copy()
        escape_character=False
        self.advance()

        escape_characters={"n":"\n","t":"\t",}

        while self.current_char!=None and (self.current_char!='"' or escape_character):
            if escape_character:
                string+=escape_characters.get(self.current_char,self.current_char)
            else:
                if self.current_char=="\\":
                    escape_character=True
                else:
                    string+=self.current_char
            self.advance()
            escape_character=False

        self.advance()
        return Token(T_STRING,string,start,self.pos)

    def make_identifier(self):
        id_string=""
        start=self.pos.copy()

        while self.current_char!=None and self.current_char in LETTERS_DIGITS+"_":
            id_string+=self.current_char
            self.advance()

        if id_string in KEYWORD:
            tok_type=T_KEYWORD
        else:
            tok_type=T_IDENTIFIER

        return Token(tok_type,id_string,start,self.pos)

    def make_divide(self):
        tok_type=T_DIVIDE
        start=self.pos.copy()
        self.advance()

        if self.current_char=="/":
            self.advance()
            tok_type=T_FLOORDIVIDE
        
        return Token(tok_type,start=start,end=self.pos)

    def make_not_equals(self):
        start=self.pos.copy()
        self.advance()

        if self.current_char=="=":
            self.advance()
            return Token(T_NE,start=start,end=self.pos)
        
        self.advance()
        return None,ExpectedCharError(start,self.pos,"'=' after '!'")

    def make_equals(self):
        tok_type=T_EQUAL
        start=self.pos.copy()
        self.advance()

        if self.current_char=="=":
            self.advance()
            tok_type=T_EE
        
        return Token(tok_type,start=start,end=self.pos)

    def make_less_than(self):
        tok_type=T_LT
        start=self.pos.copy()
        self.advance()

        if self.current_char=="=":
            self.advance()
            tok_type=T_LTE
        
        return Token(tok_type,start=start,end=self.pos)

    def make_greater_than(self):
        tok_type=T_GT
        start=self.pos.copy()
        self.advance()

        if self.current_char=="=":
            self.advance()
            tok_type=T_GTE
        
        return Token(tok_type,start=start,end=self.pos)

    def create_tokens(self):
        tokens=[]

        while self.current_char!=None:
            if self.current_char in " \t":
                self.advance()
            elif self.current_char in ";\n":
                tokens.append(Token(T_NEWLINE,start=self.pos))
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
            elif self.current_char=='"':
                tokens.append(self.make_string())
            elif self.current_char=="+":
                tokens.append(Token(T_PLUS,start=self.pos))
                self.advance()
            elif self.current_char=="-":
                tokens.append(Token(T_MINUS,start=self.pos))
                self.advance()
            elif self.current_char=="*":
                tokens.append(Token(T_MULTIPLY,start=self.pos))
                self.advance()
            elif self.current_char=="/":
                tokens.append(self.make_divide())
            elif self.current_char=="%":
                tokens.append(Token(T_MODULO,start=self.pos))
                self.advance()  
            elif self.current_char=="?":
                tokens.append(Token(T_INDEX,start=self.pos))
                self.advance()
            elif self.current_char==":":
                tokens.append(Token(T_COLON,start=self.pos))
                self.advance()
            elif self.current_char=="^":
                tokens.append(Token(T_POWER,start=self.pos))
                self.advance()
            elif self.current_char=="(":
                tokens.append(Token(T_LPAREN,start=self.pos))
                self.advance()
            elif self.current_char==")":
                tokens.append(Token(T_RPAREN,start=self.pos))
                self.advance()
            elif self.current_char=="{":
                tokens.append(Token(T_LPAREN2,start=self.pos))
                self.advance()
            elif self.current_char=="}":
                tokens.append(Token(T_RPAREN2,start=self.pos))
                self.advance()
            elif self.current_char=="[":
                tokens.append(Token(T_LPAREN3,start=self.pos))
                self.advance()
            elif self.current_char=="]":
                tokens.append(Token(T_RPAREN3,start=self.pos))
                self.advance()
            elif self.current_char==",":
                tokens.append(Token(T_COMMA,start=self.pos))
                self.advance()
            elif self.current_char=="!":
                tok,error=self.make_not_equals()
                if error:
                    return [],error
                tokens.append(tok)
            elif self.current_char=="=":
                tokens.append(self.make_equals())
            elif self.current_char=="<":
                tokens.append(self.make_less_than())
            elif self.current_char==">":
                tokens.append(self.make_greater_than())
            else:
                start=self.pos.copy()
                char=self.current_char
                self.advance()
                return [],IllegalCharacterError(start,self.pos,"'"+char+"'")
        tokens.append(Token(T_EOF,start=self.pos))
        return tokens,None

#Nodes Classes
class NumberNode():
    def __init__(self,tok):
        self.tok=tok
        self.start=self.tok.start
        self.end=self.tok.end
    
    def __repr__(self):
        return f'{self.tok}'

class StringNode():
    def __init__(self,tok):
        self.tok=tok
        self.start=self.tok.start
        self.end=self.tok.end
    
    def __repr__(self):
        return f'{self.tok}'

class ListNode():
    def __init__(self,element_nodes,start,end):
        self.element_nodes=element_nodes
        self.start=start
        self.end=end

class DictionaryNode():
    def __init__(self,key_nodes,value_nodes,start,end):
        self.key_nodes=key_nodes
        self.value_nodes=value_nodes
        self.start=start
        self.end=end
        
class VarAccessNode:
    def __init__(self,var_name_tok):
        self.var_name_tok=var_name_tok
        self.start=self.var_name_tok.start
        self.end=self.var_name_tok.end

class VarAssignNode:
    def __init__(self,var_name_tok,value_node):
        self.var_name_tok=var_name_tok
        self.value_node=value_node
        self.start=self.var_name_tok.start
        self.end=self.var_name_tok.end


class BinaryOpnode:
    def __init__(self,left_node,operator,right_node):
        self.left_node=left_node
        self.operator=operator
        self.right_node=right_node
        self.start=self.left_node.start
        self.end=self.right_node.end

    def __repr__(self):
        return f'({self.left_node},{self.operator},{self.right_node})'

class UnaryOpnode:
    def __init__(self,operator,node):
        self.operator=operator
        self.node=node
        self.start=self.operator.start
        self.end=node.end

    def __repr__(self):
        return f'({self.operator},{self.node})'

class IfNode:
    def __init__(self,cases,else_case):
        self.cases=cases
        self.else_case=else_case

        self.start=self.cases[0][0].start
        self.end=(self.else_case or self.cases[len(self.cases)-1])[0].end

class ForNode:
    def __init__(self,var_name_tok,start_value_node,end_value_node,step_value_node,body_node,return_null):
        self.var_name_tok=var_name_tok
        self.start_value_node=start_value_node
        self.end_value_node=end_value_node
        self.step_value_node=step_value_node
        self.body_node=body_node
        self.return_null=return_null

        self.start=self.var_name_tok.start
        self.end=self.body_node.end

class WhileNode:
    def __init__(self,condition_node,body_node,return_null):
        self.condition_node=condition_node
        self.body_node=body_node

        self.start=self.condition_node.start
        self.end=self.body_node.end
        self.return_null=return_null

class FuncDefNode:
    def __init__(self,var_name_tok,arg_name_toks,body_node,return_null):
        self.var_name_tok=var_name_tok
        self.arg_name_toks=arg_name_toks
        self.body_node=body_node
        self.return_null=return_null

        if self.var_name_tok:
            self.start=self.var_name_tok.start
        elif len(self.arg_name_toks)>0:
            self.start=self.arg_name_toks[0].start
        else:
            self.start=self.body_node.start

        self.end=self.body_node.end

class CallNode:
    def __init__(self,node_to_call,arg_nodes):
        self.node_to_call=node_to_call
        self.arg_nodes=arg_nodes

        self.start=self.node_to_call.start

        if len(self.arg_nodes)>0:
            self.end=self.arg_nodes[len(self.arg_nodes)-1].end
        else:
            self.end=self.node_to_call.end

#Parse Result
class ParseResult:
    def __init__(self):
        self.error=None
        self.node=None
        self.last_registered_advance_count=0
        self.advance_count=0
        self.to_reverse_count=0

    def register_advancement(self):
        self.last_registered_advance_count=1
        self.advance_count+=1
    
    def register(self,res):
        self.last_registered_advance_count=res.advance_count
        self.advance_count+=res.advance_count
        if res.error:
            self.error=res.error
        return res.node

    def try_register(self,res):
        if res.error:
            self.to_reverse_count=res.advance_count
            return None
        return self.register(res)

    def success(self,node):
        self.node=node
        return self

    def failure(self,error):
        if not self.error or self.last_registered_advance_count==0:
            self.error=error
        return self

#Parser Class
class Parser:
    def __init__(self,tokens):
        self.tokens=tokens
        self.token_index=-1
        self.advance()
    
    def advance(self):
        self.token_index+=1
        self.update_current_tok()
        return self.current_tok

    def reverse(self,amount=1):
        self.token_index-=amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.token_index<len(self.tokens):
            self.current_tok=self.tokens[self.token_index]

    def parse(self):
        res=self.statements()
        if not res.error and self.current_tok.type!=T_EOF:
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '+','-','*' or '/'"))
        return res

    def statements(self):
        res=ParseResult()
        statements=[]
        start=self.current_tok.start.copy()

        while self.current_tok.type==T_NEWLINE:
            res.register_advancement()
            self.advance()

        statement=res.register(self.expression())
        if res.error:
            return res
        statements.append(statement)

        more_statements=True

        while True:
            newline_count=0
            while self.current_tok.type==T_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count+=1
            if newline_count==0:
                more_statements=False

            if not more_statements:
                break
            statement=res.try_register(self.expression())

            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements=False
                continue
            statements.append(statement)
        
        return res.success(ListNode(statements,start,self.current_tok.end.copy()))

    def list_expression(self):
        res=ParseResult()
        element_nodes=[]
        start=self.current_tok.start.copy

        if self.current_tok.type!=T_LPAREN3:
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected '['"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type==T_RPAREN3:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expression()))
            if res.error:
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,
                "Expected ']','take', 'whether', 'StartCycle', 'AsLongAs','Method', int, float, identifier"))

            while self.current_tok.type==T_COMMA:
                res.register_advancement()
                self.advance()

                element_nodes.append(res.register(self.expression()))
                if res.error:
                    return res
            if self.current_tok.type!=T_RPAREN3:
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected ',' or '],"))
        
            res.register_advancement()
            self.advance()
        
        return res.success(ListNode(element_nodes,start,self.current_tok.end.copy()))

    def dictionary_expression(self):
        res=ParseResult()
        key_nodes=[]
        value_nodes=[]
        start=self.current_tok.start.copy

        if self.current_tok.type!=T_LPAREN2:
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '{'"))
        res.register_advancement()
        self.advance()

        if self.current_tok.type==T_RPAREN2:
            res.register_advancement()
            self.advance()

        else:
            key_nodes.append(res.register(self.expression()))
            if res.error:
                return res
            
            if self.current_tok.type!=T_COLON:
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected ':'"))
            
            res.register_advancement()
            self.advance()

            value_nodes.append(res.register(self.expression()))
            if res.error:
                return res

            while self.current_tok.type==T_COMMA:
                res.register_advancement()
                self.advance()

                key_nodes.append(res.register(self.expression()))
                if res.error:
                    return res
            
                if self.current_tok.type!=T_COLON:
                    return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected ':'"))
            
                res.register_advancement()
                self.advance()

                value_nodes.append(res.register(self.expression()))
                if res.error:
                    return res
            
            if self.current_tok.type!=T_RPAREN2:
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '}'"))

            res.register_advancement()
            self.advance()
        return res.success(DictionaryNode(key_nodes,value_nodes,start,self.current_tok.end.copy()))

    def for_expression(self):
        res=ParseResult()
        if not self.current_tok.matches(T_KEYWORD,"StartCycle"):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected 'StartCycle'"))
        res.register_advancement()
        self.advance()

        if self.current_tok.type not in (T_IDENTIFIER,):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected identifier"))

        var_name=self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type not in (T_EQUAL,):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected '='"))

        res.register_advancement()
        self.advance()

        start_value=res.register(self.expression())
        if res.error:
            return res

        if not self.current_tok.type in (T_COLON,):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected ':'"))
        res.register_advancement()
        self.advance()

        end_value=res.register(self.expression())
        if res.error:
            return res

        if self.current_tok.type in (T_COLON,):
            res.register_advancement()
            self.advance()

            step_value=res.register(self.expression())
            if res.error:
                return res
        else:
            step_value=None

        if self.current_tok.type not in (T_LPAREN2):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '{'"))
        res.register_advancement()
        self.advance()

        if self.current_tok.type in (T_NEWLINE,):
            res.register_advancement()
            self.advance()

            body=res.register(self.statements())
            if res.error:
                return res

            if self.current_tok.type not in (T_RPAREN2,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '}'"))
   
            res.register_advancement()
            self.advance()

            return res.success(ForNode(var_name,start_value,end_value,step_value,body,True))
        
        body=res.register(self.expression())
        if res.error:
            return res

        return res.success(ForNode(var_name,start_value,end_value,step_value,body,False))

    def while_expression(self):
        res=ParseResult()

        if not self.current_tok.matches(T_KEYWORD,"AsLongAs"):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected 'AsLongAs'"))
        res.register_advancement()
        self.advance()

        if self.current_tok.type not in (T_LPAREN,):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '('"))
        res.register_advancement()
        self.advance()

        condition=res.register(self.expression())
        if res.error:
            return res
        
        if self.current_tok.type in (T_RPAREN,):
            res.register_advancement()
            self.advance()
        
        if self.current_tok.type not in (T_LPAREN2):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '{'"))
        res.register_advancement()
        self.advance()

        if self.current_tok.type in (T_NEWLINE,):
            res.register_advancement()
            self.advance()
            
            body=res.register(self.expression())
            if res.error:
             return res

            if self.current_tok.type not in (T_RPAREN2,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '}'"))
            res.register_advancement()
            self.advance()

            return res.success(WhileNode(condition,body,True))

        body=res.register(self.expression())
        if res.error:
            return res

        if self.current_tok.type not in (T_RPAREN2,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '}'"))
        res.register_advancement()
        self.advance()
        
        return res.success(WhileNode(condition,body,False))
        
    def if_expression(self):
        res=ParseResult()
        all_cases=res.register(self.if_expression_cases("whether"))
        if res.error:
            return res
        cases,else_case=all_cases
        return res.success(IfNode(cases,else_case))

    def if_expression_c(self):
        res=ParseResult()
        else_case=None

        if self.current_tok.matches(T_KEYWORD,"ifnot"):
            res.register_advancement()
            self.advance()

            if not self.current_tok.type in (T_LPAREN2,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '{'"))

            res.register_advancement()
            self.advance()

            if self.current_tok.type in (T_NEWLINE,):
                res.register_advancement()
                self.advance()

                statements=res.register(self.statements())
                if res.error:
                    return res

                else_case=(statements,True)

                if self.current_tok.type in (T_RPAREN2,):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '}'"))
            else:
                expression=res.register(self.expression())
                if res.error:
                    return res
                else_case=(expression,False)

                if self.current_tok.type not in (T_RPAREN2,):
                    return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '}'"))

                res.register_advancement()
                self.advance()
        return res.success(else_case)

    def if_expression_b(self):
        return self.if_expression_cases("further")

    def if_expression_b_or_c(self):
        res=ParseResult()
        cases,else_case=[],None

        if self.current_tok.matches(T_KEYWORD,"further"):
            all_cases=res.register(self.if_expression_b())
            if res.error:
                return res
            cases,else_case=all_cases
        else:
            else_case=res.register(self.if_expression_c())
            if res.error:
                return res

        return res.success((cases,else_case))

    def if_expression_cases(self,case_keyword):
        res=ParseResult()
        cases=[]
        else_case=None

        if not self.current_tok.matches(T_KEYWORD,case_keyword):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,
            f"Expected '{case_keyword}"))

        res.register_advancement()
        self.advance()

        condition=res.register(self.expression())
        if res.error:
            return res

        if not self.current_tok.type in (T_LPAREN2,):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '{'"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type in (T_NEWLINE,):
            res.register_advancement()
            self.advance()

            statements=res.register(self.statements())
            if res.error:
                return res

            cases.append((condition,statements,True))

            if self.current_tok.type in (T_RPAREN2,):
                res.register_advancement()
                self.advance()
            else:
                all_cases=res.register(self.if_expression_b_or_c())
                if res.error:
                    return res
                new_cases,else_case=all_cases
                cases.extend(new_cases)
        else:
            expression=res.register(self.expression())
            if res.error:
                return res

            cases.append((condition,expression,False))

            all_cases=res.register(self.if_expression_b_or_c())
            if res.error:
                return res
            new_cases,else_case=all_cases
            cases.extend(new_cases)

            if self.current_tok.type not in (T_RPAREN2,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '}'"))

            res.register_advancement()
            self.advance()
        
        return res.success((cases,else_case))


    def call(self):
        res=ParseResult()
        complex=res.register(self.complex())
        if res.error:
            return res

        if self.current_tok.type in (T_LPAREN,):
            res.register_advancement()
            self.advance()

            arg_nodes=[]

            if self.current_tok.type in (T_RPAREN,):
                res.register_advancement()
                self.advance()

            else:
                arg_nodes.append(res.register(self.expression()))
                if res.error:
                    return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,
                    "Expected ')', 'take', 'whether', 'StartCycle','AsLongAs','Method','int','float','identifier'",))

                while self.current_tok.type in (T_COMMA,):
                    res.register_advancement()
                    self.advance()

                    arg_nodes.append(res.register(self.expression()))

                if self.current_tok.type in (T_RPAREN,):
                    res.register_advancement()
                    self.advance()
            return res.success(CallNode(complex,arg_nodes))
        return res.success(complex)

    def complex(self):
        res=ParseResult()
        tok=self.current_tok

        if tok.type in (T_INT,T_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type in (T_STRING,):
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type==T_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type==T_LPAREN:
            res.register_advancement()
            self.advance()
            expression=res.register(self.expression())
            if res.error:
                return res
            if self.current_tok.type==T_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expression)
            else:
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected ')'"))

        elif tok.type==T_LPAREN3:
            list_expression=res.register(self.list_expression())
            if res.error:
                return res
            return res.success(list_expression)

        elif tok.type==T_LPAREN2:
            dictionary_expression=res.register(self.dictionary_expression())
            if res.error:
                return res
            return res.success(dictionary_expression)

        elif tok.matches(T_KEYWORD,"whether"):
            if_expression=res.register(self.if_expression())
            if res.error:
                return res
            return res.success(if_expression)
        
        elif tok.matches(T_KEYWORD,"StartCycle"):
            for_expression=res.register(self.for_expression())
            if res.error:
                return res
            return res.success(for_expression)

        elif tok.matches(T_KEYWORD,"AsLongAs"):
            while_expression=res.register(self.while_expression())
            if res.error:
                return res
            return res.success(while_expression)

        elif tok.matches(T_KEYWORD,"Method"):
            func_def=res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        return res.failure(InvalidSyntaxError(tok.start,tok.end,"Expected int,float,identifier,'+','-' or '('"))

    def power(self):
        return self.BinaryOperation(self.call,(T_POWER,),self.factor)

    def factor(self):
        res=ParseResult()
        tok=self.current_tok

        if tok.type in (T_PLUS,T_MINUS):
            res.register_advancement()
            self.advance()
            factor=res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpnode(tok,factor))

        return self.power()

    def term(self):
        return self.BinaryOperation(self.factor,(T_MULTIPLY,T_DIVIDE,T_INDEX,T_FLOORDIVIDE,T_MODULO))

    def comp_expression(self):
        res=ParseResult()

        if self.current_tok.matches(T_KEYWORD,"not"):
            operator=self.current_tok
            res.register_advancement()
            self.advance()

            node=res.register(self.comp_expression())
            if res.error:
                return res
            
            return res.success(UnaryOpnode(operator,node))

        node=res.register(self.BinaryOperation(self.arith_expression,(T_EE,T_NE,T_LT,T_LTE,T_GT,T_GTE)))

        if res.error:
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,
            "Expected int, float, identifier, '+', '-', '(', 'not'"))

        return res.success(node)

    def arith_expression(self):
        return self.BinaryOperation(self.term,(T_PLUS,T_MINUS))

    def expression(self):
        res=ParseResult()
        if self.current_tok.matches(T_KEYWORD,"take"):
            res.register_advancement()
            self.advance()

            if self.current_tok.type!=T_IDENTIFIER:
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected Identifier"))

            var_name=self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type not in (T_EQUAL,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '='"))
            res.register_advancement()
            self.advance()
            
            expression=res.register(self.expression())
            if res.error:
                return res
            return res.success(VarAssignNode(var_name,expression))
            
        node=res.register(self.BinaryOperation(self.comp_expression,((T_KEYWORD,"and"),(T_KEYWORD,"or"))))

        if res.error:
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,
            "Expected 'take', int, float, identifier, '+', '-', '*', '/'"))
        return res.success(node)

    def func_def(self):
        res=ParseResult()

        if not self.current_tok.matches(T_KEYWORD,"Method"):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected 'Method'"))
        res.register_advancement()
        self.advance()

        if self.current_tok.type in (T_IDENTIFIER,):
            var_name_tok=self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type not in (T_LPAREN,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '('"))
        else:
            var_name_tok=None
            if self.current_tok.type not in (T_LPAREN,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected identifier or '('"))

        res.register_advancement()
        self.advance()

        arg_name_toks=[]

        if self.current_tok.type in (T_IDENTIFIER,):
            arg_name_toks.append(self.current_tok)
            res.register_advancement()
            self.advance()

            while self.current_tok.type in (T_COMMA,):
                res.register_advancement()
                self.advance()

                if self.current_tok.type not in (T_IDENTIFIER,):
                    return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected identifier"))

                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()
        
            if self.current_tok.type not in (T_RPAREN,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected ',' or ')'"))

        else:
            if self.current_tok.type not in (T_RPAREN,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected identifier or ')'"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type in (T_LPAREN2):
            res.register_advancement()
            self.advance()

            body=res.register(self.expression())
            if res.error:
                return res

            if self.current_tok.type not in (T_RPAREN2,):
                return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,f"Expected identifier or ')'"))

            res.register_advancement()
            self.advance()

            return(res.success(FuncDefNode(var_name_tok,arg_name_toks,body,False)))

        if self.current_tok.type not in (T_NEWLINE,):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '{' or Newline"))

        res.register_advancement()
        self.advance() 

        body=res.register(self.statements())

        if res.error:
            return res

        if self.current_tok.type not in (T_RPAREN2,):
            return res.failure(InvalidSyntaxError(self.current_tok.start,self.current_tok.end,"Expected '}'"))

        res.register_advancement()
        self.advance()

        return(res.success(FuncDefNode(var_name_tok,arg_name_toks,body,True)))


    def BinaryOperation(self,function1,operators,function2=None):
        if function2==None:
            function2=function1
        res=ParseResult()
        left=res.register(function1())
        if res.error:
            return res

        while self.current_tok.type in operators or (self.current_tok.type,self.current_tok.value) in operators:
            operator=self.current_tok
            res.register_advancement()
            self.advance()
            right=res.register(function2())
            if res.error:
                return res
            left=BinaryOpnode(left,operator,right)

        return res.success(left)


#RunTimeResult Class
class RunTimeResult:
    def __init__(self):
        self.value=None
        self.error=None
    
    def register(self,res):
        if res.error:
            self.error=res.error
        return res.value
    
    def success(self,value):
        self.value=value
        return self

    def failure(self,error):
        self.error=error
        return self

#Value Class
class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()
    
    def set_pos(self,start=None,end=None):
        self.start=start
        self.end=end
        return self

    def set_context(self,context=None):
        self.context=context
        return self

    def add(self,other):
        return None,self.illegal_operation(other)
    
    def subtract(self,other):
        return None,self.illegal_operation(other)

    def multiply(self,other):
        return None,self.illegal_operation(other)

    def divide(self,other):
        return None,self.illegal_operation(other)
    
    def floor_divide(self,other):
        return None,self.illegal_operation(other)

    def modulo(self,other):
        return None,self.illegal_operation(other)

    def power(self,other):
        return None,self.illegal_operation(other)

    def comparison_equal(self,other):
        return None,self.illegal_operation(other)

    def comparison_notequal(self,other):
        return None,self.illegal_operation(other)

    def comparison_lessthanequal(self,other):
        return None,self.illegal_operation(other)

    def comparison_greaterthanequal(self,other):
        return None,self.illegal_operation(other)

    def comparison_greaterthan(self,other):
        return None,self.illegal_operation(other)

    def comparison_lessthan(self,other):
        return None,self.illegal_operation(other)

    def andop(self,other):
        return None,self.illegal_operation(other)

    def orop(self,other):
        return None,self.illegal_operation(other)

    def notop(self):
        return None,self.illegal_operation()

    def execute(self,args):
        return RunTimeResult().failure(self.illegal_operation())

    def copy(self):
        raise Exception("No Copy Method Defined")

    def is_true(self):
        return False

    def illegal_operation(self,other=None):
        if not other:
            other=self
        return RunTimeError(self.start,other.end,"Illegal Operation",self.context)

#Number Class
class Number(Value):
    def __init__(self,value):
        super().__init__()
        self.value=value

    def add(self,other):
        if isinstance(other,Number):
            return Number(self.value+other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def subtract(self,other):
        if isinstance(other,Number):
            return Number(self.value-other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def multiply(self,other):
        if isinstance(other,Number):
            return Number(self.value*other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def divide(self,other):
        if isinstance(other,Number):
            if other.value==0:
                return None,RunTimeError(other.start,other.end,"Division By Zero",self.context)
            return Number(self.value/other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def floor_divide(self,other):
        if isinstance(other,Number):
            if other.value==0:
                return None,RunTimeError(other.start,other.end,"Division By Zero",self.context)
            return Number(self.value//other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def modulo(self,other):
        if isinstance(other,Number):
            if other.value==0:
                return None,RunTimeError(other.start,other.end,"Modulo By Zero",self.context)
            return Number(self.value%other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def power(self,other):
        if isinstance(other,Number):
            return Number(self.value**other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def comparison_equal(self,other):
        if isinstance(other,Number):
            return Number(int(self.value==other.value)).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def comparison_notequal(self,other):
        if isinstance(other,Number):
            return Number(int(self.value!=other.value)).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def comparison_lessthanequal(self,other):
        if isinstance(other,Number):
            return Number(int(self.value<=other.value)).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def comparison_greaterthanequal(self,other):
        if isinstance(other,Number):
            return Number(int(self.value>=other.value)).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def comparison_greaterthan(self,other):
        if isinstance(other,Number):
            return Number(int(self.value>other.value)).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def comparison_lessthan(self,other):
        if isinstance(other,Number):
            return Number(int(self.value<other.value)).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def andop(self,other):
        if isinstance(other,Number):
            return Number(int(self.value and other.value)).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def orop(self,other):
        if isinstance(other,Number):
            return Number(int(self.value or other.value)).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def notop(self):
        return Number(1 if self.value==0 else 0).set_context(self.context),None

    def copy(self):
        copy=Number(self.value)
        copy.set_pos(self.start,self.end)
        copy.set_context(self.context)
        return copy

    def is_true(self):
        return self.value!=0
    
    def __repr__(self):
        return str(self.value)

Number.null=Number(0)
Number.false=Number(0)
Number.true=Number(1)

class  String(Value):
    def __init__(self,value):
        super().__init__()
        self.value=value

    def add(self,other):
        if isinstance(other,String):
            return String(self.value+other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def multiply(self, other):
        if isinstance(other,Number):
            return String(self.value*other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def index(self, other):
        if isinstance(other,Number):
            try:
                if other.value==0:
                    return None,RunTimeError(other.start,other.end,'String index out of range',self.context)
                elif other.value>0:
                    other.value-=1
                return String(self.value[other.value]).set_context(self.context),None
            except:
                return None,RunTimeError(other.start,other.end,'String index out of range',self.context)
        elif isinstance(other,List):
            try:
                word=''
                for i in other.elements:
                    if i.value==0:
                        return None,RunTimeError(other.start,other.end,'String index out of range',self.context)
                    elif i.value>0:
                        i.value-=1
                    word+=self.value[i.value]
                return String(word).set_context(self.context),None
            except:
                return None,RunTimeError(other.start,other.end,'String index out of range',self.context)
        else:
            return None,Value.illegal_operation(self,other)

    def  is_true(self):
        return len(self.value)>0

    def copy(self):
        copy=String(self.value)
        copy.set_pos(self.start,self.end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return self.value
        
    def __repr__(self) -> str:
        return f'"{self.value}"'

class List(Value):
    def __init__(self,elements):
        super().__init__()
        self.elements=elements

    def add(self,other):
        if isinstance(other,List):
            return List(self.elements+other.elements).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def subtract(self, other):
        if isinstance(other,Number):
            new_list=self.copy()
            try:
                new_list.elements.pop(other.value)
                return new_list,None
            except:
                return None,RunTimeError(other.start,other.end,'List index out of range',self.context)
        else:
            return None,Value.illegal_operation(self,other)

    def multiply(self, other):
        if isinstance(other,Number):
            return List(self.elements*other.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def index(self, other):
        if isinstance(other,Number):
            try:
                if other.value==0:
                    return None,RunTimeError(other.start,other.end,'List index out of range',self.context)
                elif other.value>0:
                    other.value-=1
                if isinstance(self.elements[other.value],String):
                    return String(self.elements[other.value].value).set_context(self.context),None
                elif isinstance(self.elements[other.value],Number):
                    return Number(self.elements[other.value]).set_context(self.context),None
            except:
                return None,RunTimeError(other.start,other.end,'List index out of range',self.context)
        elif isinstance(other,List):
            try:
                listresult=[]
                for i in other.elements:
                    if i.value==0:
                        return None,RunTimeError(other.start,other.end,'List index out of range',self.context)
                    elif i.value>0:
                        i.value-=1
                    listresult.append(self.elements[i.value])
                return List(listresult).set_context(self.context),None
            except:
                return None,RunTimeError(other.start,other.end,'List index out of range',self.context)
        else:
            return None,Value.illegal_operation(self,other)

    def copy(self):
        copy=List(self.elements)
        copy.set_pos(self.start,self.end)
        copy.set_context(self.context)
        return copy

    def __str__(self):
        return ", ".join([str(x) for x in self.elements])

    def __repr__(self):
        return f'[{", ".join([repr(x) for x in self.elements])}]'

class Dictionary(Value):
    def __init__(self,key,value):
        super().__init__()
        self.key=key
        self.value=value
        self.key_value=[]

        for i in range(len(self.key)):
            self.key_value.append((self.key[i],self.value[i]))

    def add(self,other):
        if isinstance(other,List):
            self.key.append(other.elements[0])
            self.value.append(other.elements[1])

            return Dictionary(self.key,self.value).set_context(self.context),None
        else:
            return None,Value.illegal_operation(self,other)

    def copy(self):
        copy=Dictionary(self.key,self.value)
        copy.set_pos(self.start,self.end)
        copy.set_context(self.context)
        return copy

    def __str__(self) -> str:
        return ",".join([str(x[0])+':'+str(x[1]) for x in self.key_value])

    def __repr__(self):
        return "{"+",".join([str(x[0])+':'+str(x[1]) for x in self.key_value])+"}"

class BaseFunction(Value):
    def __init__(self,name):
        super().__init__()
        self.name=name or "<anonymous>"

    def generate_new_context(self):
        new_context=Context(self.name,self.context,self.start)
        new_context.symbol_table=SymbolTable(new_context.parent.symbol_table)
        return new_context

    def check_args(self,arg_names,args):
        res=RunTimeResult()
        if len(args)>len(arg_names):
            return res.failure(RunTimeError(self.start,self.end,
            f"{len(args)-len(arg_names)} excess arguments are passed into '{self}'",self.context))

        if len(args)<len(arg_names):
            return res.failure(RunTimeError(self.start,self.end,
            f"{len(arg_names)-len(args)} less arguments are passed into '{self}'",self.context))

        return res.success(None)

    def populate_args(self,arg_names,args,exec_ctx):
        for i in range(len(args)):
            arg_name=arg_names[i]
            arg_value=args[i]
            arg_value.set_context(exec_ctx)
            exec_ctx.symbol_table.set(arg_name,arg_value)

    def check_and_populate_args(self,arg_names,args,exec_ctx):
        res=RunTimeResult()
        res.register(self.check_args(arg_names,args))
        if res.error:
            return res
        self.populate_args(arg_names,args,exec_ctx)
        return res.success(None)

class Function(BaseFunction):
    def __init__(self,name,body_node,arg_names,return_null):
        super().__init__(name)
        self.body_node=body_node
        self.arg_names=arg_names
        self.return_null=return_null

    def execute(self, args):
        res=RunTimeResult()
        interpreter=Interpreter()
        exec_ctx=self.generate_new_context()

        res.register(self.check_and_populate_args(self.arg_names,args,exec_ctx))
        if res.error:
            return res

        value=res.register(interpreter.visit(self.body_node,exec_ctx))
        if res.error:
            return res
        return res.success(Number.null if self.return_null else value)

    def copy(self):
        copy=Function(self.name,self.body_node,self.arg_names,self.return_null)
        copy.set_context(self.context)
        copy.set_pos(self.start,self.end)
        return copy

    def __repr__(self):
        return f"<function>{self.name}"

class BuiltInFunction(BaseFunction):
    def __init__(self, name):
        super().__init__(name)

    def execute(self,args):
        res=RunTimeResult()
        exec_ctx=self.generate_new_context()

        method_name=f'execute_{self.name}'
        method=getattr(self,method_name,self.no_visit_method)

        res.register(self.check_and_populate_args(method.arg_names,args,exec_ctx))
        if res.error:
            return res

        return_value=res.register(method(exec_ctx))
        if res.error:
            return res

        return res.success(return_value)

    def no_visit_method(self,node,context):
        raise Exception(f'No execute_{self.name} method defined')

    def copy(self):
        copy=BuiltInFunction(self.name)
        copy.set_context(self.context)
        copy.set_pos(self.start,self.end)
        return copy

    def __repr__(self):
        return f"<built-in function{self.name}>"

    def execute_print(self,exec_ctx):
        print(str(exec_ctx.symbol_table.get("value")))
        return RunTimeResult().success(Number.null)

    execute_print.arg_names=["value"]

    def execute_input(self,exec_ctx):
        text=input()
        return RunTimeResult().success(String(text))

    execute_input.arg_names=[]

    def execute_input_int(self,exec_ctx):
        while True:
            text=input()
            try:
                number=int(text)
                break
            except ValueError:
                print(f"'{text}' must be an integer")
        return RunTimeResult().success(Number(number))

    execute_input_int.arg_names=[]

    def execute_is_number(self,exec_ctx):
        is_number=isinstance(exec_ctx.symbol_table.get("value"),Number)
        return RunTimeResult().success(Number.true if is_number else Number.false)

    execute_is_number.arg_names=["value"]

    def execute_is_string(self,exec_ctx):
        is_number=isinstance(exec_ctx.symbol_table.get("value"),String)
        return RunTimeResult().success(Number.true if is_number else Number.false)

    execute_is_string.arg_names=["value"]

    def execute_is_list(self,exec_ctx):
        is_list=isinstance(exec_ctx.symbol_table.get("value"),List)
        return RunTimeResult().success(Number.true if is_list else Number.false)

    execute_is_list.arg_names=["value"]

    def execute_append(self,exec_ctx):
        list_=exec_ctx.symbol_table.get("list")
        value=exec_ctx.symbol_table.get("value")

        if not isinstance(list_,List):
            return RunTimeResult().failure(RunTimeError(self.start,self.end,
            "First argument must be a list",exec_ctx))

        list_.elements.append(value)
        return RunTimeResult().success(Number.null)
    execute_append.arg_names=["list","value"]

    def execute_pop(self,exec_ctx):
        list_=exec_ctx.symbol_table.get("list")
        index=exec_ctx.symbol_table.get("index")

        if not isinstance(list_,List):
            return RunTimeResult().failure(RunTimeError(self.start,self.end,
            "First argument must be a list",exec_ctx))

        if not isinstance(index,Number):
            return RunTimeResult().failure(RunTimeError(self.start,self.end,
            "Second argument must be an integer",exec_ctx))

        try:
            if index.value>0:
                index.value-=1
            element=list_.elements.pop(index.value)
        except:
            return RunTimeResult().failure(RuntimeError(self.start,self.end,"List index out of range",exec_ctx))
        return RunTimeResult().success(element)

    execute_pop.arg_names=["list","index"]

    def execute_extend(self,exec_ctx):
        listA=exec_ctx.symbol_table.get("listA")
        listB=exec_ctx.symbol_table.get("listB")

        if not isinstance(listA,List):
            return RunTimeResult().failure(RunTimeError(self.start,self.end,
            "First argument must be a list",exec_ctx))

        if not isinstance(listB,List):
            return RunTimeResult().failure(RunTimeError(self.start,self.end,
            "Second argument must be a list",exec_ctx))

        listA.elements.extend(listB.elements)
        return RunTimeResult().success(Number.null)

    execute_extend.arg_names=["listA","listB"]

BuiltInFunction.print=BuiltInFunction("print")
BuiltInFunction.input=BuiltInFunction("input")
BuiltInFunction.input_int=BuiltInFunction("input_int")
BuiltInFunction.is_number=BuiltInFunction("is_number")
BuiltInFunction.is_string=BuiltInFunction("is_string")
BuiltInFunction.is_list=BuiltInFunction("is_list")
BuiltInFunction.append=BuiltInFunction("append")
BuiltInFunction.pop=BuiltInFunction("pop")
BuiltInFunction.extend=BuiltInFunction("extend")
    
#Context Class
class Context:
    def __init__(self,display_name,parent=None,parent_pos=None):
        self.display_name=display_name
        self.parent=parent
        self.parent_pos=parent_pos
        self.symbol_table=None

#SymbolTable
class SymbolTable:
    def __init__(self,parent=None):
        self.symbols={}
        self.parent=parent
    
    def get(self,name):
        value=self.symbols.get(name,None)
        if value==None and self.parent:
            return self.parent.get(name)
        return value

    def set(self,name,value):
        self.symbols[name]=value

    def remove(self,name):
        del self.symbols[name]

#Interpreter Class
class Interpreter():
    def visit(self,node,context):
        method_name=f'visit_{type(node).__name__}'
        method=getattr(self,method_name,self.no_visit_method)
        return method(node,context)

    def no_visit_method(self,node,context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

    def visit_NumberNode(self,node,context):
        return RunTimeResult().success(Number(node.tok.value).set_context(context).set_pos(node.start,node.end))

    def visit_VarAccessNode(self,node,context):
        res=RunTimeResult()
        var_name=node.var_name_tok.value
        value=context.symbol_table.get(var_name)

        if not value:
            return res.failure(RunTimeError(node.start,node.end,f"'{var_name}' is not defined",context))

        value=value.copy().set_pos(node.start,node.end).set_context(context)
        return res.success(value)

    def visit_VarAssignNode(self,node,context):
        res=RunTimeResult()
        var_name=node.var_name_tok.value
        value=res.register(self.visit(node.value_node,context))
        if res.error:
            return res
        context.symbol_table.set(var_name,value)
        return res.success(value)

    def visit_BinaryOpnode(self,node,context):
        res=RunTimeResult()
        left=res.register(self.visit(node.left_node,context))
        if res.error:
            return res
        right=res.register(self.visit(node.right_node,context))
        if res.error:
            return res

        if node.operator.type==T_PLUS:
            result,error=left.add(right)
        elif node.operator.type==T_MINUS:
            result,error=left.subtract(right)
        elif node.operator.type==T_MULTIPLY:
            result,error=left.multiply(right)
        elif node.operator.type==T_DIVIDE:
            result,error=left.divide(right)
        elif node.operator.type==T_FLOORDIVIDE:
            result,error=left.floor_divide(right)
        elif node.operator.type==T_MODULO:
            result,error=left.modulo(right)
        elif node.operator.type==T_INDEX:
            result,error=left.index(right)
        elif node.operator.type==T_POWER:
            result,error=left.power(right)
        elif node.operator.type==T_EE:
            result,error=left.comparison_equal(right)
        elif node.operator.type==T_NE:
            result,error=left.comparison_notequal(right)
        elif node.operator.type==T_LT:
            result,error=left.comparison_lessthan(right)
        elif node.operator.type==T_LTE:
            result,error=left.comparison_lessthanequal(right)
        elif node.operator.type==T_GT:
            result,error=left.comparison_greaterthan(right)
        elif node.operator.type==T_GTE:
            result,error=left.comparison_greaterthanequal(right)
        elif node.operator.matches(T_KEYWORD,"and"):
            result,error=left.andop(right)
        elif node.operator.matches(T_KEYWORD,"or"):
            result,error=left.orop(right)
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.start,node.end))

    def visit_UnaryOpnode(self,node,context):
        res=RunTimeResult()
        number=res.register(self.visit(node.node,context))
        if res.error:
            return res
        error=None
        if node.operator.type==T_MINUS:
            number,error=number.multiply(Number(-1))
        elif node.operator.matches(T_KEYWORD,"not"):
            number,error=number.notop()
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.start,node.end))

    def visit_StringNode(self,node,context):
        return RunTimeResult().success(String(node.tok.value).set_context(context).set_pos(node.start,node.end))

    def visit_ListNode(self,node,context):
        res=RunTimeResult()
        elements=[]

        for element_node in node.element_nodes:
            elements.append(res.register(self.visit(element_node,context)))
            if res.error:
                return res
        return res.success(List(elements).set_context(context).set_pos(node.start,node.end))

    def visit_DictionaryNode(self,node,context):
        res=RunTimeResult()
        key=[]
        value=[]

        for key_node in node.key_nodes:
            key.append(res.register(self.visit(key_node,context)))
            if res.error:
                return res
        
        for value_node in node.value_nodes:
            value.append(res.register(self.visit(value_node,context)))
            if res.error:
                return res

        return res.success(Dictionary(key,value).set_context(context).set_pos(node.start,node.end))

    def visit_IfNode(self,node,context):
        res=RunTimeResult()

        for condition,expression,return_null in node.cases:
            condition_value=res.register(self.visit(condition,context))
            if res.error:
                return res
            if condition_value.is_true():
                expression_value=res.register(self.visit(expression,context))
                if res.error:
                    return res
                return res.success(Number.null if return_null else expression_value)
        
        if node.else_case:
            expression,return_null=node.else_case
            else_value=res.register(self.visit(expression,context))
            if res.error:
                return res
            return res.success(Number.null if return_null else else_value)

        return res.success(Number.null)

    def visit_ForNode(self,node,context):
        res=RunTimeResult()
        elements=[]

        start_value=res.register(self.visit(node.start_value_node,context))
        if res.error:
            return res

        end_value=res.register(self.visit(node.end_value_node,context))
        if res.error:
            return res
        
        if node.step_value_node:
            step_value=res.register(self.visit(node.step_value_node,context))
            if res.error:
                return res
        else:
            step_value=Number(1)
        
        i=start_value.value

        if step_value.value>=0:
            condition=lambda:i<=end_value.value
        else:
            condition=lambda:i>=end_value.value

        while condition():
            context.symbol_table.set(node.var_name_tok.value,Number(i))
            i+=step_value.value

            elements.append(res.register(self.visit(node.body_node,context)))
            if res.error:
                return res

        return res.success(Number.null if node.return_null else List(elements).set_context(context).set_pos(node.start,node.end))

    def visit_WhileNode(self,node,context):
        res=RunTimeResult()
        elements=[]

        while True:
            condition=res.register(self.visit(node.condition_node,context))
            if res.error:
                return res
            
            if not condition.is_true():
                break

            elements.append(res.register(self.visit(node.body_node,context)))
            if res.error:
                return res
                
        return res.success(Number.null if node.return_null else List(elements).set_context(context).set_pos(node.start,node.end))

    def visit_FuncDefNode(self,node,context):
        res=RunTimeResult()
        if node.var_name_tok:
            func_name=node.var_name_tok.value
        else:
            func_name=None
        body_node=node.body_node
        arg_names=[arg_name.value for arg_name in node.arg_name_toks]
        func_value=Function(func_name,body_node,arg_names,node.return_null).set_context(context).set_pos(node.start,node.end)

        if node.var_name_tok:
            context.symbol_table.set(func_name,func_value)

        return res.success(func_value)

    def visit_CallNode(self,node,context):
        res=RunTimeResult()
        args=[]

        value_to_call=res.register(self.visit(node.node_to_call,context))
        
        if res.error:
            return res
        value_to_call=value_to_call.copy().set_pos(node.start,node.end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node,context)))
            if res.error:
                return res

        return_value=res.register(value_to_call.execute(args))
        if res.error:
            return res
        return_value=return_value.copy().set_pos(node.start,node.end).set_context(context)
        return res.success(return_value)

global_symbol_table=SymbolTable()
global_symbol_table.set("Null",Number.null)
global_symbol_table.set("True",Number.true)
global_symbol_table.set("False",Number.false)
global_symbol_table.set("Print",BuiltInFunction.print)
global_symbol_table.set("Input",BuiltInFunction.input)
global_symbol_table.set("Input_Int",BuiltInFunction.input_int)
global_symbol_table.set("Is_number",BuiltInFunction.is_number)
global_symbol_table.set("Is_string",BuiltInFunction.is_string)
global_symbol_table.set("Is_list",BuiltInFunction.is_list)
global_symbol_table.set("Append",BuiltInFunction.append)
global_symbol_table.set("Pop",BuiltInFunction.pop)
global_symbol_table.set("Extend",BuiltInFunction.extend)


#Run Method
def run(filename,text):
    #Generate Tokens
    lexer=Lexer(filename,text)
    tokens,error=lexer.create_tokens()

    if error:
        return None,error

    #Generate Abstract Syntax Tree
    parser=Parser(tokens)
    ast=parser.parse()

    if ast.error:
        return None,ast.error

    interpreter=Interpreter()
    context=Context("<program>")
    context.symbol_table=global_symbol_table
    result=interpreter.visit(ast.node,context)

    return result.value,result.error

'''try:
    with open("MyProgram.txt","r") as file:
        script=file.read()
except Exception as e:
        print("Failed to load script"+str(e))

result,errors=run("MyProgram.txt",script)

if errors:
    print(errors.show_error())
elif result:
    print(result)'''

#Codes
'''while True:
    text=input("code> ")
    if text=="q":
        break
    result,errors=run("<stdin>",text)
    if errors:
        print(errors.show_error())
    elif result:
        print(result)'''