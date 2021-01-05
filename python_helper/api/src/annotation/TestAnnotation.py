from python_helper.api.src.domain import Constant as c
from python_helper.api.src.service import LogHelper, ReflectionHelper, EnvironmentHelper, ObjectHelper
from python_helper.api.src.annotation.EnvironmentAnnotation import EnvironmentVariable

CALL_BEFORE = 'callBefore'
ARGS_OF_CALL_BEFORE = 'argsOfCallBefore'
KWARGS_OF_CALL_BEFORE = 'kwargsOfCallBefore'
CALL_AFTER = 'callAfter'
ARGS_OF_CALL_AFTER = 'argsOfCallAfter'
KWARGS_OF_CALL_AFTER = 'kwargsOfCallAfter'
RETURN_VALUE_FROM_CALL_BEFORE = 'returnOfCallBefore'
RETURN_VALUE_FROM_CALL_AFTER = 'returnOfCallAfter'

TEST_VALUE_NOT_SET = '__TEST_VALUE_NOT_SET__'
BEFORE_THE_TEST = 'before'
AFTER_THE_TEST = 'after'

def Test(
    *outerArgs,
    environmentVariables = None,
    callBefore = TEST_VALUE_NOT_SET,
    argsOfCallBefore = TEST_VALUE_NOT_SET,
    kwargsOfCallBefore = TEST_VALUE_NOT_SET,
    callAfter = TEST_VALUE_NOT_SET,
    argsOfCallAfter = TEST_VALUE_NOT_SET,
    kwargsOfCallAfter = TEST_VALUE_NOT_SET,
    returns = None,
    **outerKwargs
) :
    def innerMethodWrapper(resourceInstanceMethod,*innerMethodArgs,**innerMethodKwargs) :
        @EnvironmentVariable(environmentVariables=environmentVariables)
        def innerResourceInstanceMethod(*innerArgs,**innerKwargs) :
            methodReturnException = None
            methodReturn = TEST_VALUE_NOT_SET
            handleBefore(resourceInstanceMethod, callBefore, argsOfCallBefore, kwargsOfCallBefore, returns)
            try :
                methodReturn = resourceInstanceMethod(*innerArgs,**innerKwargs)
                LogHelper.printSuccess(f'{ReflectionHelper.getName(resourceInstanceMethod)} test succeed', condition=True)
            except Exception as exception :
                methodReturnException = exception
                LogHelper.printError(f'"{ReflectionHelper.getName(resourceInstanceMethod)}" test failed', condition=True, exception=methodReturnException)
            return handleAfter(resourceInstanceMethod, callAfter, argsOfCallAfter, kwargsOfCallAfter, returns, methodReturn, methodReturnException=methodReturnException)
        ReflectionHelper.overrideSignatures(innerResourceInstanceMethod, resourceInstanceMethod)
        return innerResourceInstanceMethod
    return innerMethodWrapper

def handleBefore(resourceInstanceMethod, actionClass, args, kwargs, returns) :
    LogHelper.test(resourceInstanceMethod, 'Test started')
    actionHandlerException = handle(resourceInstanceMethod, actionClass, args, kwargs, returns, BEFORE_THE_TEST, RETURN_VALUE_FROM_CALL_BEFORE)
    if ObjectHelper.isNotNone(actionHandlerException) :
        raise actionHandlerException

def handleAfter(resourceInstanceMethod, actionClass, args, kwargs, returns, methodReturn, methodReturnException=None) :
    actionHandlerException = handle(resourceInstanceMethod, actionClass, args, kwargs, returns, AFTER_THE_TEST, RETURN_VALUE_FROM_CALL_AFTER)
    LogHelper.test(resourceInstanceMethod, 'Test completed')
    if ObjectHelper.isNotNone(methodReturnException) or ObjectHelper.isNotNone(actionHandlerException) :
        if ObjectHelper.isNotNone(methodReturnException) and ObjectHelper.isNotNone(actionHandlerException) :
            raise Exception(f'{LogHelper.getExceptionMessage(methodReturnException)}. Followed by: {LogHelper.getExceptionMessage(actionHandlerException)}')
        elif ObjectHelper.isNotNone(methodReturnException) :
            raise methodReturnException
        raise actionHandlerException
    if not TEST_VALUE_NOT_SET == methodReturn :
        return methodReturn

def handle(resourceInstanceMethod, actionClass, args, kwargs, returns, moment, returnKey) :
    try :
        returnCall = None
        if actionIsPresent(actionClass) :
            argsMessage = getArgsLogMessage(args)
            kwargsMessage = getKwargsLogMessage(kwargs)
            returnCall = getRetrunValue(actionClass, args, kwargs)
            LogHelper.test(resourceInstanceMethod, f'{ReflectionHelper.getName(actionClass)}({argsMessage}, {kwargsMessage}): {returnCall}')
        else :
            LogHelper.test(resourceInstanceMethod, f'Test handler to perform actions {moment} the test is not defined')
        if returnsValueIsPresent(returns) :
            returns[returnKey] = returnCall
    except Exception as exception :
        LogHelper.printError(f'"{ReflectionHelper.getName(resourceInstanceMethod)}" test went wrong while handling actions {moment} the test. Check TEST logs for more information', condition=True, exception=exception)
        return exception

def getArgsLogMessage(args) :
    if TEST_VALUE_NOT_SET == args :
        return '*()'
    return f'*({args})'

def getKwargsLogMessage(kwargs) :
    if TEST_VALUE_NOT_SET == kwargs :
        return '**{}'
    return f'**{kwargs}'

def getRetrunValue(actionClass, givenArgs, givenKwargs) :
    if actionIsPresent(actionClass) :
        args = [] if TEST_VALUE_NOT_SET == givenArgs else givenArgs
        kwargs = {} if TEST_VALUE_NOT_SET == givenKwargs else givenKwargs
        return actionClass(*args, **kwargs)

def actionIsPresent(actionClass) :
    return not TEST_VALUE_NOT_SET == actionClass and ObjectHelper.isNotNone(actionClass)

def returnsValueIsPresent(returns) :
    isPresent = ObjectHelper.isDictionary(returns)
    if not isPresent :
        LogHelper.test(returnsValueIsPresent, f'the key "returns" from "{ReflectionHelper.getName(Test)}" annotation call was not defined')
    return isPresent