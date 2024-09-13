USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Dms_Rsrc_L]    Script Date: 2022-02-11 ¿ÀÀü 9:34:39 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Dms_Rsrc_L](
	[Inst_Name] [varchar](100) NOT NULL,
	[Task_Name] [varchar](100) NOT NULL,
	[CollectDT] [varchar](8) NOT NULL,
	[CollectHH] [varchar](2) NOT NULL,
	[Rsrc_Name] [varchar](100) NOT NULL,
	[Rsrc_Val] [decimal](15, 2) NOT NULL,
	[CollectDTM] [datetime] NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL
) ON [PRIMARY]
GO


