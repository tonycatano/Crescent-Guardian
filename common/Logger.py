import logging
import inspect

#--------------------------------------------------------------------------
# Custom logging functions
#--------------------------------------------------------------------------
class Logger():
  logger        = None
  initialized   = False
  debugMode     = False
  eventLogFile  = "logs/rocg.event.log"
  logFormat     = '%(asctime)s.%(msecs)03d-UTC [%(levelname)s] '\
                  '%(moduleName)s.%(className)s.%(functionName)s(): %(message)s'
  dateFormat    = '%Y-%m-%d %H:%M:%S'
  extra         = {'moduleName':'NoModuleName', 'className':'NoClassName', 'functionName':'NoFunctionName'}

  def initLogger(loggerName:str) -> None:
    if not Logger.initialized:
      formatter   = logging.Formatter(Logger.logFormat, Logger.dateFormat)
      
      fileHandler = logging.FileHandler(Logger.eventLogFile)
      fileHandler.setLevel(logging.DEBUG)
      fileHandler.setFormatter(formatter)
      
      streamHandler = logging.StreamHandler()
      streamHandler.setLevel(logging.ERROR)
      streamHandler.setFormatter(formatter)

      Logger.logger = logging.getLogger(loggerName)
      Logger.logger.setLevel(logging.DEBUG)
      Logger.logger.addHandler(fileHandler)
      Logger.logger.addHandler(streamHandler)
      Logger.logger.propagate = False

      from common.common import getDevOption
      Logger.debugMode = getDevOption('debugMode')
      Logger.initialized = True

  def loggerDecorator(func):
    def wrapper(*args, **kwargs):
      frame = inspect.stack()[1]
      moduleName   = inspect.getmodulename(frame.filename) if inspect.getmodulename(frame.filename) else "NoModuleName"
      className    = args[0].__class__.__name__ if args[0].__class__.__name__ else "NoClassName"
      functionName = frame.function if frame.function else "NoFunctionName"
      Logger.extra = {'moduleName':moduleName, 'className':className, 'functionName':functionName}
      func(*args, **kwargs)
    return wrapper

  @loggerDecorator
  def logDebug(obj:object, msg:str) -> None:
    if Logger.debugMode:
      Logger.logger.debug(msg, extra=Logger.extra)

  @loggerDecorator
  def logInfo(obj:object, msg:str) -> None:
    Logger.logger.info(msg, extra=Logger.extra)

  @loggerDecorator
  def logWarning(obj:object, msg:str) -> None:
    Logger.logger.warning(msg, extra=Logger.extra)

  @loggerDecorator
  def logError(obj:object, msg:str) -> None:
    Logger.logger.error(msg, extra=Logger.extra)

  @loggerDecorator
  def logCritical(obj:object, msg:str) -> None:
    Logger.logger.critical(msg, extra=Logger.extra)
