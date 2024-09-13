USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Ora_Alert_Chk_L]    Script Date: 2022-02-11 ¿ÀÀü 9:29:58 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Ora_Alert_Chk_L](
	[hostName] [varchar](30) NOT NULL,
	[IPAddr] [varchar](15) NOT NULL,
	[CollectDT] [varchar](8) NOT NULL,
	[CollectHH] [varchar](2) NOT NULL,
	[Seq] [int] NOT NULL,
	[MESSAGE_TEXT] [varchar](2048) NOT NULL,
	[MODULE_ID] [varchar](30) NULL,
	[PROBLEM_KEY] [varchar](500) NULL,
	[DETAILED_LOCATION] [varchar](150) NULL,
	[CollectDTM] [datetime] NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_Ora_Alert_Chk_L] PRIMARY KEY CLUSTERED 
(
	[CollectDT] ASC,
	[CollectHH] ASC,
	[hostName] ASC,
	[IPAddr] ASC,
	[Seq] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


