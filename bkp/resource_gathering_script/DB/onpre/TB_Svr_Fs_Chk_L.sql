USE [MonitoringDB]
GO

/****** Object:  Table [dbo].[TB_Svr_Fs_Chk_L]    Script Date: 2022-02-11 ¿ÀÀü 9:30:24 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[TB_Svr_Fs_Chk_L](
	[CollectDT] [varchar](8) NOT NULL,
	[hostName] [varchar](30) NOT NULL,
	[path_name] [varchar](100) NOT NULL,
	[use_pct] [decimal](5, 2) NOT NULL,
	[RGPR_ID] [varchar](30) NULL,
	[RGST_DTM] [datetime] NULL,
	[MDFPR_ID] [varchar](30) NULL,
	[MDF_DTM] [datetime] NULL,
	[NOTE] [varchar](100) NULL,
 CONSTRAINT [PK_Svr_Fs_Chk_L] PRIMARY KEY CLUSTERED 
(
	[CollectDT] ASC,
	[hostName] ASC,
	[path_name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO


